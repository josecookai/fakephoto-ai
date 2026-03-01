import { FC } from 'react'
import { Github, ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'

const CTA: FC = () => {
  return (
    <section id="cta" className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="glass rounded-2xl p-12 text-center relative overflow-hidden"
        >
          {/* Background Decoration */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary-500/10 to-transparent" />

          <div className="relative z-10">
            <h2 className="text-4xl font-bold mb-4">
              Ready to Detect AI-Generated Content?
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
              Start using FakePhoto.ai today. Open source, free to use, and
              constantly improving.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href="https://github.com/josecookai/fakephoto-ai"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary flex items-center gap-2"
              >
                <Github className="w-5 h-5" />
                Get Started
                <ArrowRight className="w-4 h-4" />
              </a>
              <a href="/docs" className="btn-secondary">
                Read Documentation
              </a>
            </div>

            <p className="mt-8 text-sm text-gray-500">
              MIT Licensed • Free Forever • Community Driven
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default CTA