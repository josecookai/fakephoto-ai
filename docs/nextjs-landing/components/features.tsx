"use client"

import { motion } from "framer-motion"
import { Target, Image, Zap, Plug, Globe, BarChart3 } from "lucide-react"

const features = [
  {
    icon: Target,
    title: "Multi-Model Consensus",
    description: "Combines results from OpenAI, Gemini, and Anthropic for robust detection with weighted confidence scoring.",
  },
  {
    icon: Image,
    title: "Image & Video Support",
    description: "Analyze photos and videos with intelligent frame sampling for comprehensive authenticity verification.",
  },
  {
    icon: Zap,
    title: "Batch Processing",
    description: "Process entire folders of media files at once. Perfect for journalists, researchers, and content moderators.",
  },
  {
    icon: Plug,
    title: "API & SDK",
    description: "RESTful API and Python SDK for seamless integration into your applications and workflows.",
  },
  {
    icon: Globe,
    title: "Web Interface",
    description: "Beautiful, intuitive Streamlit UI for quick drag-and-drop analysis without any coding required.",
  },
  {
    icon: BarChart3,
    title: "Detailed Reports",
    description: "Get comprehensive analysis with specific indicators: lighting, textures, facial anomalies, metadata.",
  },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
    },
  },
}

export function Features() {
  return (
    <section id="features" className="py-24 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
            Why FakePhoto.ai?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Advanced detection powered by multiple state-of-the-art AI models
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              variants={itemVariants}
              className="group relative p-6 rounded-2xl bg-secondary/50 border border-border/50 hover:border-primary/30 transition-all duration-300 hover:-translate-y-1"
            >
              {/* Top gradient line */}
              <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 scale-x-0 group-hover:scale-x-100 transition-transform duration-300 rounded-t-2xl" />
              
              <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white mb-4 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300">
                <feature.icon className="w-7 h-7" />
              </div>
              
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}