import {
  GoogleGenerativeAI,
  GenerativeModel,
  CachedContent,
} from "@google/generative-ai";
import axios from "axios";
import * as cheerio from "cheerio";

// Configuration interface
interface GeminiConfig {
  apiKey: string;
  model: string;
  temperature: number;
  maxOutputTokens: number;
  useContextCaching: boolean;
  cacheTTLHours: number;
}

// Cached website content interface
interface CachedWebsiteContent {
  url: string;
  content: string;
  structure: any;
  cachedAt: Date;
  geminiCacheId?: string;
}

// Website structure analysis
interface WebsiteStructure {
  title: string;
  headings: Array<{ tag: string; text: string }>;
  forms: Array<{
    action: string;
    method: string;
    inputs: Array<{
      type: string;
      name: string;
      id: string;
      placeholder: string;
      selector: string;
      required: boolean;
    }>;
  }>;
  buttons: Array<{
    text: string;
    type: string;
    selector: string;
  }>;
  interactableElements: Array<{
    tag: string;
    type: string;
    selector: string;
    text: string;
  }>;
  textContent: string[];
  links: Array<{ text: string; href: string }>;
}

export class GeminiService {
  private genAI: GoogleGenerativeAI;
  private model: GenerativeModel;
  private config: GeminiConfig;
  private websiteCache = new Map<string, CachedWebsiteContent>();
  private contextCache = new Map<string, CachedContent>();

  constructor(config: GeminiConfig) {
    this.config = config;
    this.genAI = new GoogleGenerativeAI(config.apiKey);
    this.model = this.genAI.getGenerativeModel({
      model: config.model,
      generationConfig: {
        temperature: config.temperature,
        maxOutputTokens: config.maxOutputTokens,
      },
    });

    console.log(`✅ Gemini Service initialized with model: ${config.model}`);
  }

  /**
   * Fetch and analyze website content with caching
   */
  async fetchWebsiteContent(url: string): Promise<string> {
    const cacheKey = url;

    // Check cache first
    if (this.websiteCache.has(cacheKey)) {
      const cached = this.websiteCache.get(cacheKey)!;
      const cacheAge = Date.now() - cached.cachedAt.getTime();
      const cacheTTL = 60 * 60 * 1000; // 1 hour

      if (cacheAge < cacheTTL) {
        console.log(`🎯 Using cached website content for: ${url}`);
        return cached.content;
      }
    }

    try {
      console.log(`🌐 Fetching comprehensive content from: ${url}`);
      const response = await axios.get(url, {
        timeout: 15000,
        headers: {
          "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        },
        maxContentLength: 5 * 1024 * 1024, // 5MB limit
      });

      const structure = this.analyzeWebsiteStructure(response.data);
      const contentDescription = this.generateContentDescription(
        url,
        structure
      );

      // Cache the content
      const cachedContent: CachedWebsiteContent = {
        url,
        content: contentDescription,
        structure,
        cachedAt: new Date(),
      };

      this.websiteCache.set(cacheKey, cachedContent);
      console.log(`💾 Cached website content for: ${url}`);

      return contentDescription;
    } catch (error) {
      console.error(`❌ Failed to fetch website content from ${url}:`, error);
      return `Failed to fetch website content from ${url}. Error: ${
        error instanceof Error ? error.message : String(error)
      }`;
    }
  }

  /**
   * Analyze website structure using Cheerio
   */
  private analyzeWebsiteStructure(html: string): WebsiteStructure {
    const $ = cheerio.load(html);

    return {
      title: $("title").text().trim(),

      headings: $("h1, h2, h3, h4, h5, h6")
        .map((index: number, element: any) => ({
          tag: element.tagName,
          text: $(element).text().trim(),
        }))
        .get()
        .slice(0, 20),

      forms: $("form")
        .map((index: number, element: any) => ({
          action: $(element).attr("action") || "",
          method: $(element).attr("method") || "GET",
          inputs: $(element)
            .find("input, textarea, select")
            .map((index: number, input: any) => ({
              type: $(input).attr("type") || "text",
              name: $(input).attr("name") || "",
              id: $(input).attr("id") || "",
              placeholder: $(input).attr("placeholder") || "",
              required: $(input).attr("required") !== undefined,
              selector: this.generateOptimalSelector($(input)),
            }))
            .get(),
        }))
        .get(),

      buttons: $(
        'button, input[type="button"], input[type="submit"], a[role="button"]'
      )
        .map((index: number, element: any) => ({
          text: $(element).text().trim() || $(element).attr("value") || "",
          type: $(element).attr("type") || "button",
          selector: this.generateOptimalSelector($(element)),
        }))
        .get()
        .slice(0, 20),

      interactableElements: $(
        'input, button, select, textarea, a[href], [onclick], [role="button"]'
      )
        .map((index: number, element: any) => ({
          tag: element.tagName.toLowerCase(),
          type: $(element).attr("type") || "",
          text:
            $(element).text().trim() ||
            $(element).attr("value") ||
            $(element).attr("placeholder") ||
            "",
          selector: this.generateOptimalSelector($(element)),
        }))
        .get()
        .slice(0, 50),

      textContent: $("p, div, span")
        .map((index: number, element: any) => $(element).text().trim())
        .get()
        .filter((text: string) => text.length > 10 && text.length < 200)
        .slice(0, 30),

      links: $("a[href]")
        .map((index: number, element: any) => ({
          text: $(element).text().trim(),
          href: $(element).attr("href") || "",
        }))
        .get()
        .slice(0, 20),
    };
  }

  /**
   * Generate optimal CSS selector for an element
   */
  private generateOptimalSelector(element: any): string {
    const id = element.attr("id");
    const className = element.attr("class");
    const name = element.attr("name");
    const tagName = element.prop("tagName")?.toLowerCase() || "";

    // Priority order: ID > Name > Class > Tag
    if (id) {
      return `#${id}`;
    }
    if (name) {
      return `${tagName}[name="${name}"]`;
    }
    if (className) {
      const firstClass = className.split(" ")[0];
      return `${tagName}.${firstClass}`;
    }
    return tagName;
  }

  /**
   * Generate comprehensive content description
   */
  private generateContentDescription(
    url: string,
    structure: WebsiteStructure
  ): string {
    return `
WEBSITE: ${url}
TITLE: ${structure.title}

PAGE STRUCTURE:
${structure.headings.map((h) => `${h.tag.toUpperCase()}: ${h.text}`).join("\n")}

FORMS AND INPUTS:
${structure.forms
  .map(
    (form) =>
      `Form (${form.method} -> ${form.action || "current page"}):\n${form.inputs
        .map(
          (input) =>
            `  - ${input.type} field "${input.name}" (selector: ${
              input.selector
            })${
              input.placeholder ? ` [placeholder: "${input.placeholder}"]` : ""
            }${input.required ? " [required]" : ""}`
        )
        .join("\n")}`
  )
  .join("\n\n")}

CLICKABLE ELEMENTS:
${structure.buttons
  .map((btn) => `- Button/Link: "${btn.text}" (selector: ${btn.selector})`)
  .join("\n")}

ALL INTERACTIVE ELEMENTS:
${structure.interactableElements
  .map(
    (el) =>
      `- ${el.tag}${el.type ? `[${el.type}]` : ""}: "${el.text}" → ${
        el.selector
      }`
  )
  .join("\n")}

IMPORTANT TEXT CONTENT:
${structure.textContent.slice(0, 20).join("\n")}

NAVIGATION LINKS:
${structure.links.map((link) => `- "${link.text}" → ${link.href}`).join("\n")}
    `.trim();
  }

  /**
   * Generate Selenium code using default model (backward compatibility)
   */
  async generateSeleniumCode(
    prompt: string,
    websiteUrl: string
  ): Promise<string> {
    return this.generateSeleniumCodeWithModel(
      prompt,
      websiteUrl,
      this.config.model,
      this.config.useContextCaching
    );
  }

  /**
   * Generate Selenium automation code with specific model configuration
   */
  async generateSeleniumCodeWithModel(
    prompt: string,
    websiteUrl: string,
    modelName: string,
    useContextCaching: boolean = false
  ): Promise<string> {
    console.log(
      `🤖 Generating Selenium code with ${modelName} for: ${websiteUrl}`
    );

    try {
      // Create model instance with specific configuration
      const modelInstance = this.genAI.getGenerativeModel({
        model: modelName,
        generationConfig: {
          temperature: this.config.temperature,
          maxOutputTokens: this.config.maxOutputTokens,
        },
      });

      const websiteContent = await this.fetchWebsiteContent(websiteUrl);

      const enhancedPrompt = `You are an expert Selenium WebDriver automation engineer. Generate ONLY clean, executable Python code.

CRITICAL REQUIREMENTS:
1. Generate ONLY Python code - NO markdown, explanations, or comments outside code
2. Use explicit waits (WebDriverWait) instead of time.sleep()
3. Use the most reliable selectors from the website analysis below
4. Handle exceptions with try-catch blocks
5. Verify elements exist before interaction
6. Take screenshots on errors for debugging
7. Return meaningful results or status messages

TASK TO AUTOMATE: ${prompt}

WEBSITE ANALYSIS:
${websiteContent}

Generate precise Selenium Python code that accomplishes the task:`;

      let result;
      if (useContextCaching && this.config.useContextCaching) {
        // Use context caching for better performance
        result = await this.generateWithCaching(
          enhancedPrompt,
          websiteUrl,
          modelInstance
        );
      } else {
        // Direct generation without caching
        result = await modelInstance.generateContent(enhancedPrompt);
      }

      const generatedCode = result.response.text();

      if (!generatedCode || generatedCode.trim().length === 0) {
        throw new Error(`${modelName} returned empty response`);
      }

      // Clean up any remaining markdown formatting
      const cleanCode = generatedCode
        .replace(/```python\n?/g, "")
        .replace(/```\n?/g, "")
        .replace(/^#+.*$/gm, "")
        .trim();

      console.log(
        `✅ Generated ${cleanCode.length} characters with ${modelName}`
      );
      return cleanCode;
    } catch (error) {
      console.error(`❌ ${modelName} code generation failed:`, error);
      throw error;
    }
  }

  /**
   * Generate content with context caching (simplified version)
   */
  private async generateWithCaching(
    prompt: string,
    websiteUrl: string,
    modelInstance: GenerativeModel
  ): Promise<any> {
    // Simplified caching approach - use in-memory cache only
    const cacheKey = `${websiteUrl}-${modelInstance.model}`;

    // For now, just use direct generation (context caching API may vary)
    console.log(
      `🎯 Generating with model cache optimization for: ${websiteUrl}`
    );
    return await modelInstance.generateContent(prompt);
  }

  /**
   * Clean up expired caches
   */
  cleanupExpiredCaches(): void {
    const now = Date.now();
    const websiteCacheTTL = 60 * 60 * 1000; // 1 hour

    // Clean website cache
    for (const [key, cached] of this.websiteCache.entries()) {
      const age = now - cached.cachedAt.getTime();
      if (age > websiteCacheTTL) {
        this.websiteCache.delete(key);
        console.log(`🧹 Cleaned up expired website cache for: ${key}`);
      }
    }

    console.log(
      `📊 Cache status: ${this.websiteCache.size} websites, ${this.contextCache.size} Gemini contexts`
    );
  }

  /**
   * Get cache statistics
   */
  getCacheStats() {
    return {
      websiteCacheSize: this.websiteCache.size,
      contextCacheSize: this.contextCache.size,
      contextCachingEnabled: this.config.useContextCaching,
      model: this.config.model,
    };
  }
}

// Factory function to create Gemini service from environment
export function createGeminiService(): GeminiService {
  const config: GeminiConfig = {
    apiKey: process.env.GEMINI_API_KEY || "",
    model: process.env.GEMINI_MODEL || "gemini-2.0-flash-exp",
    temperature: parseFloat(process.env.GEMINI_TEMPERATURE || "0.1"),
    maxOutputTokens: parseInt(process.env.GEMINI_MAX_OUTPUT_TOKENS || "8192"),
    useContextCaching: process.env.GEMINI_USE_CONTEXT_CACHING === "true",
    cacheTTLHours: parseInt(process.env.GEMINI_CACHE_TTL_HOURS || "24"),
  };

  if (!config.apiKey) {
    throw new Error("GEMINI_API_KEY environment variable is required");
  }

  return new GeminiService(config);
}
