import { FC } from 'react'
import { Shield, Github, Twitter, Mail } from 'lucide-react'

const Footer: FC = () => {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    Product: [
      { name: 'Features', href: '#features' },
      { name: 'API Docs', href: '/docs' },
      { name: 'Pricing', href: '#' },
      { name: 'Changelog', href: '#' },
    ],
    Resources: [
      { name: 'Documentation', href: '/docs' },
      { name: 'GitHub', href: 'https://github.com/josecookai/fakephoto-ai' },
      { name: 'Examples', href: '#' },
      { name: 'Blog', href: '#' },
    ],
    Company: [
      { name: 'About', href: '#' },
      { name: 'Contact', href: '#' },
      { name: 'Privacy', href: '#' },
      { name: 'Terms', href: '#' },
    ],
  }

  const socialLinks = [
    { name: 'GitHub', icon: Github, href: 'https://github.com/josecookai/fakephoto-ai' },
    { name: 'Twitter', icon: Twitter, href: 'https://twitter.com/fakephotoai' },
    { name: 'Email', icon: Mail, href: 'mailto:team@fakephoto.ai' },
  ]

  return (
    <footer className="border-t border-white/10 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <a href="/" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">
                FakePhoto.ai
              </span>
            </a>
            <p className="text-gray-400 mb-6 max-w-sm">
              Multi-Model AI Detection Engine for verifying the authenticity of
              images and videos.
            </p>

            {/* Social Links */}
            <div className="flex items-center gap-4">
              {socialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
                  aria-label={social.name}
                >
                  <social.icon className="w-5 h-5" />
                </a>
              ))}
            </div>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="font-semibold mb-4">{category}</h4>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom */}
        <div className="pt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-gray-500 text-sm">
            {currentYear} FakePhoto.ai. All rights reserved.
          </p>
          <p className="text-gray-500 text-sm">
            Made with ❤️ by the FakePhoto.ai team
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer