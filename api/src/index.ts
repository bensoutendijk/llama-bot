import Fastify, { FastifyInstance, FastifyReply, FastifyRequest } from 'fastify'
import fastifyPostgres from '@fastify/postgres'
import fastifyJwt from '@fastify/jwt'
import { config } from 'dotenv'

config() // Load environment variables

const fastify: FastifyInstance = Fastify({
  logger: true
})

// Register PostgreSQL plugin
fastify.register(fastifyPostgres, {
  connectionString: process.env.DATABASE_URL
})

// Register JWT plugin
fastify.register(fastifyJwt, {
  secret: process.env.JWT_SECRET || 'your-secret-key'
})

// Declare routes
fastify.get('/', async (request, reply) => {
  reply.send({ hello: 'world' })
})

fastify.post('/register', async (request: FastifyRequest, reply: FastifyReply) => {
  const { username, password } = request.body as { username: string, password: string }
  
  try {
    const result = await fastify.pg.query(
      'SELECT * FROM tavern.register_user($1, $2)',
      [username, password]
    )
    const user = result.rows[0]
    
    reply.send({ message: 'User registered successfully', userId: user.id })
  } catch (error) {
    reply.status(400).send({ error: 'Registration failed' })
  }
})

fastify.post('/login', async (request: FastifyRequest, reply: FastifyReply) => {
  const { username, password } = request.body as { username: string, password: string }
  
  try {
    const result = await fastify.pg.query(
      'SELECT * FROM tavern.authenticate($1, $2)',
      [username, password]
    )
    const user = result.rows[0]
    
    if (user) {
      const token = fastify.jwt.sign({ userId: user.id, username: user.username })
      reply.send({ token })
    } else {
      reply.status(401).send({ error: 'Invalid credentials' })
    }
  } catch (error) {
    reply.status(400).send({ error: 'Authentication failed' })
  }
})

// Protected route example
fastify.get('/protected', {
  preHandler: fastify.auth([
    async (request: FastifyRequest, reply: FastifyReply) => {
      try {
        await request.jwtVerify()
      } catch (err) {
        reply.send(err)
      }
    }
  ])
}, async (request, reply) => {
  reply.send({ message: 'This is a protected route', user: request.user })
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
