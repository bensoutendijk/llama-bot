declare namespace NodeJS {
  interface ProcessEnv {
    TAVERN_HOSTNAME: string;
    DISCORD_CLIENT_ID: string;
    DISCORD_CLIENT_SECRET: string;
    DISCORD_REDIRECT_URI: string;
    DATABASE_URL: string;
    JWT_SECRET: string;
  }
}
