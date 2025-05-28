const { Database } = require("../lib/db");

async function initializeDatabase() {
  try {
    console.log("Initializing database...");
    await Database.init();
    console.log("Database initialized successfully!");
    process.exit(0);
  } catch (error) {
    console.error("Failed to initialize database:", error);
    process.exit(1);
  }
}

initializeDatabase();
