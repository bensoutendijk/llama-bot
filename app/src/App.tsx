import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [json, setJson] = useState<{
    hello: string
  }>({
    hello: '...'
  })

  useEffect(() => {
    fetch('/api/')
      .then((res) => res.json())
      .then((data) => {
        setJson(data)
      })
  }, [])
  
  return (
    <>
      <div>
        {json?.hello}
      </div>
    </>
  )
}

export default App
