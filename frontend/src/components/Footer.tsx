import Logo from "./Logo";

export default function Footer() {
  return (
    <footer className="relative bg-[#0A0A0A] text-white py-16 border-t border-white/10">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-x-8 gap-y-12">
          <div className="lg:col-span-3 space-y-6">
            <Logo />
            <p className="text-gray-400 text-sm leading-relaxed max-w-sm">
              Experience meaningful connections with AI companions that
              understand and care. Your journey to authentic conversations
              starts here.
            </p>
            <div className="pt-2 flex-col gap-2">
              <p className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs mb-2 font-medium bg-white/5 text-gray-300 border border-white/10">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                End-to-End Encrypted
              </p>
              <p className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-white/5 text-gray-300 border border-white/10">
                <span className="w-2 h-2 rounded-full bg-fuchsia-400"></span>
                Premium data protection
              </p>
            </div>
          </div>

          <div className="lg:col-span-9 grid grid-cols-2 md:grid-cols-4 gap-16 lg:justify-items-end lg:ml-auto">
            <div className="space-y-4 w-full">
              <h3 className="text-sm font-semibold text-white/90">Product</h3>
              <ul className="space-y-3">
                <li>
                  <a
                    href="/pricing"
                    className="text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    Pricing
                  </a>
                </li>
                <li>
                  <a
                    href="/integrations"
                    className="text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    Integrations
                  </a>
                </li>
              </ul>
            </div>

            <div className="space-y-4 w-full">
              <h3 className="text-sm font-semibold text-white/90">Resources</h3>
              <ul className="space-y-3">
                <li>
                  <a
                    href="/help"
                    className="text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    Help Center
                  </a>
                </li>
                <li>
                  <a
                    href="/contact"
                    className="text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    Contact Support
                  </a>
                </li>
              </ul>
            </div>

            <div className="space-y-4 w-full">
              <h3 className="text-sm font-semibold text-white/90">Company</h3>
              <ul className="space-y-3">
                <li>
                  <a
                    href="/about"
                    className="text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    About
                  </a>
                </li>

                <li>
                  <a
                    href="/contact"
                    className="text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    Contact
                  </a>
                </li>
              </ul>
            </div>

            <div className="space-y-4 w-full">
              <h3 className="text-sm font-semibold text-white/90">Connect</h3>
              <ul className="space-y-3">
                <li>
                  <a
                    href="https://www.tiktok.com/@chathera_officiel"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    TikTok
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.instagram.com/chathera_officiel"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    Instagram
                  </a>
                </li>
                <li>
                  <a
                    href="https://x.com/ChatheraAI"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    X (twitter)
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-16 pt-8 border-t border-white/10">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-400">
              &copy; {new Date().getFullYear()} ChatHera. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              <a href="/PrivacyPolicy" className="text-sm text-gray-400 hover:text-white transition-colors">
                Privacy Policy
              </a>
              <a href="/TermsOfServices" className="text-sm text-gray-400 hover:text-white transition-colors">
                Terms of Service
              </a>
              <a href="/Cookies" className="text-sm text-gray-400 hover:text-white transition-colors">
                Cookies
              </a>
              <a href="/LegalNotices" className="text-sm text-gray-400 hover:text-white transition-colors">
                Legal Notices
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
