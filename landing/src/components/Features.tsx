import { FC } from 'react'
import { Image, Video, Layers, Clock, Shield, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'

const features = [
  {
    icon: Image,
    title: 'Image Analysis',
    description:
      'Detect AI-generated images across all major formats including JPG, PNG, WebP, and HEIC.',
  },
  {
    icon: Video,
    title: 'Video Detection',
    description:
      'Analyze video content with intelligent frame sampling to identify deepfake patterns.',
  },
  {
    icon: Layers,
    title: 'Multi-Model Consensus',
    description:
      'Leverage the power of GPT-4V, Gemini, and Claude for comprehensive analysis.',
  },
  {
    icon: Clock,
    title: 'Fast Processing',
    description:
      'Get results in seconds with our optimized pipeline and parallel processing.',
  },
  {
    icon: Shield,
    title: 'High Accuracy',
    description:
      '97% accuracy with ensemble voting from multiple state-of-the-art AI models.',
  },
  {
    icon: Sparkles,
    title: 'Batch Processing',
    description:
      'Analyze entire folders of media files with a single command or API call.',
  },
]

const Features: FC = () => {
  return (
    <section id="features" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">
            Powerful <span className="gradient-text">Features</span>
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Everything you need to verify the authenticity of visual content
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="glass rounded-xl p-6 hover:bg-white/10 transition-colors group"
            >
              <div className="w-12 h-12 bg-primary-500/20 rounded-lg flex items-center justify-center mb-4 group-hover:bg-primary-500/30 transition-colors">
                <feature.icon className="w-6 h-6 text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Features