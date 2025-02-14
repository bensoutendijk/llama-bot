import './App.css'
import { useState } from 'react'

function App() {
  const [isLoading, setIsLoading] = useState(false);

  const handleDiscordLogin = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/auth/discord', {
        method: 'GET',
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        window.location.href = data.authorizationUrl;
      } else {
        console.error('Failed to initiate Discord login');
      }
    } catch (error) {
      console.error('Error during Discord login:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="app-container">
        <header className="header">
        <div className="logo">Logo</div>
        <button 
          className="cta-button discord-login" 
          onClick={handleDiscordLogin}
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Login with Discord'}
        </button>
      </header>

      <section className="hero">
        <div className="hero-content">
          <h1>Welcome to Our Amazing Platform</h1>
          <p>Discover the power of our innovative solutions.</p>
          <div className="cta-buttons">
            <button className="primary-cta">Get Started</button>
            <button className="secondary-cta">Learn More</button>
          </div>
        </div>
        <div className="hero-illustration">
          {/* Placeholder for illustration */}
          <div className="placeholder-image">Illustration</div>
        </div>
      </section>

      <main className="main-content">
        <section className="features">
          <h2>Our Features</h2>
          <div className="feature-list">
            <div className="feature-item">Feature 1</div>
            <div className="feature-item">Feature 2</div>
            <div className="feature-item">Feature 3</div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="footer-content">
          <p>&copy; 2024 Your Company. All rights reserved.</p>
          <div className="footer-links">
            <a href="#privacy">Privacy Policy</a>
            <a href="#terms">Terms of Service</a>
          </div>
        </div>
      </footer>
      </div>
    </div>
  )
}

export default App
