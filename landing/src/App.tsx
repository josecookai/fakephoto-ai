import { FC } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Features from './components/Features'
import HowItWorks from './components/HowItWorks'
import Models from './components/Models'
import CTA from './components/CTA'
import Footer from './components/Footer'

const App: FC = () => {
  return (
    <div className="min-h-screen bg-dark-900">
      <Navbar />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <Models />
        <CTA />
      </main>
      <Footer />
    </div>
  )
}

export default App