export interface Logger {
  info(message: string, metadata?: any): void;
  warning(message: string, metadata?: any): void;
  error(message: string, metadata?: any): void;
  debug(message: string, metadata?: any): void;
}

export function createLogger(context?: string): Logger {
  const formatMessage = (level: string, message: string, metadata?: any) => {
    const timestamp = new Date().toISOString();
    const contextStr = context ? `[${context}]` : "";
    const metadataStr = metadata ? ` ${JSON.stringify(metadata)}` : "";
    return `${timestamp} ${level.toUpperCase()}${contextStr}: ${message}${metadataStr}`;
  };

  return {
    info: (message: string, metadata?: any) => {
      console.log(formatMessage("info", message, metadata));
    },
    warning: (message: string, metadata?: any) => {
      console.warn(formatMessage("warning", message, metadata));
    },
    error: (message: string, metadata?: any) => {
      console.error(formatMessage("error", message, metadata));
    },
    debug: (message: string, metadata?: any) => {
      if (
        typeof process !== "undefined" &&
        process.env?.NODE_ENV === "development"
      ) {
        console.debug(formatMessage("debug", message, metadata));
      }
    },
  };
}
