import { FC } from 'react'
import { motion } from 'framer-motion'

const models = [
  {
    name: 'GPT-4 Vision',
    provider: 'OpenAI',
    accuracy: '94%',
    speed: 'Medium',
    bestFor: 'Complex scenes',
    color: 'from-green-400 to-green-600',
  },
  {
    name: 'Gemini Pro Vision',
    provider: 'Google',
    accuracy: '91%',
    speed: 'Fast',
    bestFor: 'Metadata analysis',
    color: 'from-blue-400 to-blue-600',
  },
  {
    name: 'Claude 3 Vision',
    provider: 'Anthropic',
    accuracy: '89%',
    speed: 'Medium',
    bestFor: 'Texture details',
    color: 'from-orange-400 to-orange-600',
  },
  {
    name: 'Ensemble',
    provider: 'FakePhoto.ai',
    accuracy: '97%',
    speed: 'Variable',
    bestFor: 'Overall detection',
    color: 'from-primary-400 to-primary-600',
    featured: true,
  },
]

const Models: FC = () => {
  return (
    <section id="models" className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">
            AI <span className="gradient-text">Models</span>
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            We combine the strengths of leading AI vision models for maximum accuracy
          </p>
        </div>

        {/* Models Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {models.map((model, index) => (
            <motion.div
              key={model.name}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`rounded-xl p-6 ${
                model.featured
                  ? 'bg-gradient-to-br from-primary-500/20 to-primary-700/20 border-2 border-primary-500/50'
                  : 'glass'
              }`}
            >
              {model.featured && (
                <div className="inline-block px-3 py-1 bg-primary-500/20 rounded-full text-xs font-semibold text-primary-300 mb-4">
                  Recommended
                </div>
              )}

              <div
                className={`w-12 h-1 rounded-full bg-gradient-to-r ${model.color} mb-4`}
              />

              <h3 className="text-lg font-semibold mb-1">{model.name}</h3>
              <p className="text-sm text-gray-400 mb-4">{model.provider}</p>

              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Accuracy</span>
                  <span className="font-semibold text-white">{model.accuracy}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Speed</span>
                  <span className="font-semibold text-white">{model.speed}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Best For</span>
                  <span className="font-semibold text-white">{model.bestFor}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Models