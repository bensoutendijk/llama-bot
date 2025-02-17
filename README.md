# Llama Bot
Connect a chatbot with various personalities to your Discord server

## Developers Guide
Follow these steps to get started

### Install Docker

### Download and install drivers on the host machine
https://developer.nvidia.com/cuda-downloads

#### If using WSL install the toolkit in WSL
https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=WSL-Ubuntu&target_version=2.0

### Configure for development
#### Copy the `.env.example` file to a new file named `.env`

```bash
cp .env.example .env
```

#### Update the variables
`TAVERN_BOT_TOKEN` Retrieve a discord bot token from https://discord.com/developers/applications
`TAVERN_OPENAI_BASE` This should 
