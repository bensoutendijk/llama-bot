import Fastify, { FastifyInstance, FastifyReply, FastifyRequest } from 'fastify'
import fastifyPostgres from '@fastify/postgres'
import fastifyJwt from '@fastify/jwt'
import fastifyAuth from '@fastify/auth'
import { FastifyAuthFunction } from '@fastify/auth'
import axios from 'axios'
import crypto from 'crypto'

// Validate environment variables
const env = {
  TAVERN_HOSTNAME: process.env.TAVERN_HOSTNAME,
  DISCORD_CLIENT_ID: process.env.DISCORD_CLIENT_ID,
  DISCORD_CLIENT_SECRET: process.env.DISCORD_CLIENT_SECRET,
  DISCORD_REDIRECT_URI: process.env.DISCORD_REDIRECT_URI,
  DATABASE_URL: process.env.DATABASE_URL,
  JWT_SECRET: process.env.JWT_SECRET
}

for (const [key, value] of Object.entries(env)) {
  if (!value) {
    throw new Error(`Missing environment variable: ${key}`)
  }
}

const fastify: FastifyInstance = Fastify({
  logger: true
})

// Register PostgreSQL plugin
fastify.register(fastifyPostgres, {
  connectionString: env.DATABASE_URL
})
.then(() => {
  fastify.log.info('PostgreSQL plugin registered successfully')
})

// Register JWT plugin
fastify.register(fastifyJwt, {
  secret: env.JWT_SECRET
})

// Register Auth plugin
fastify.register(fastifyAuth).then(() => {
  fastify.log.info('Auth plugin registered successfully')
})

// Define an authentication function
const authenticate: FastifyAuthFunction = async (request, reply) => {
  try {
    await request.jwtVerify()
  } catch (err) {
    reply.send(err)
  }
}

// Declare routes
fastify.get('/', async (request, reply) => {
  reply.send({ hello: 'world' })
})

// Discord OAuth2 routes
fastify.get('/auth/discord', async (request, reply) => {
  const state = crypto.randomBytes(16).toString('hex')
  const authorizationUrl = `https://discord.com/api/oauth2/authorize?client_id=${env.DISCORD_CLIENT_ID}&redirect_uri=${encodeURIComponent(env.DISCORD_REDIRECT_URI)}&integration_type=0&scope=identify%20bot&state=${state}`
  reply.send({ authorizationUrl })
})

fastify.get('/auth/discord/callback', async (request: FastifyRequest, reply: FastifyReply) => {
  const { code, state } = request.query as { code: string, state: string }

  try {
    // Exchange code for access token
    const tokenResponse = await axios.post('https://discord.com/api/oauth2/token', new URLSearchParams({
      client_id: env.DISCORD_CLIENT_ID,
      client_secret: env.DISCORD_CLIENT_SECRET,
      code,
      grant_type: 'authorization_code',
      redirect_uri: env.DISCORD_REDIRECT_URI,
      scope: 'identify email',
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    const { access_token, token_type } = tokenResponse.data

    // Get user information
    const userResponse = await axios.get('https://discord.com/api/users/@me', {
      headers: {
        authorization: `${token_type} ${access_token}`,
      },
    })

    const { id, username, email } = userResponse.data

    // Check if user exists in database, if not, create new user
    const result = await fastify.pg.query(
      'SELECT * FROM tavern.upsert_discord_user($1, $2, $3)',
      [id, username, email]
    )
    const user = result.rows[0]

    // Generate JWT token
    const token = fastify.jwt.sign({ userId: user.id, username: user.username })

    // Redirect to frontend with token
    reply.redirect(`${env.TAVERN_HOSTNAME}/auth-callback?token=${token}`)
  } catch (error) {
    console.error('Error during Discord authentication:', error)
    reply.status(400).send({ error: 'Authentication failed' })
  }
})

// Run the server!
const start = async () => {
  try {
    await fastify.listen({ port: 8080, host: "0.0.0.0" })
  } catch (err) {
    fastify.log.error(err)
    process.exit(1)
  }
}
start()
