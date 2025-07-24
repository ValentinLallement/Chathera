import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service | Chathera",
  description: "Read our Terms of Service to understand the rules and guidelines for using Chathera's AI-powered conversational platform.",
};

export default function TermsOfServicePage() {
  return (
    <main className="min-h-screen px-6 md:px-12 py-32 bg-background text-foreground text-white">
      <div className="max-w-4xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold tracking-tight">Terms of Service</h1>
        <p className="text-sm text-muted-foreground">
          Last updated: June 27, 2025
        </p>

        <div className="space-y-6 text-base leading-relaxed">
          <section>
            <p>
              These Terms of Service ("Terms") govern your access to and use of the website <a href="https://chathera.com" className="text-blue-600 hover:underline">https://chathera.com</a> ("Service") provided by Chathera ("we", "us", or "our"). By using the Service, you agree to be bound by these Terms and our <a href="/privacy-policy" className="text-blue-600 hover:underline">Privacy Policy</a>.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">1. Legal Information</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Company Name:</strong> Chathera</li>
              <li><strong>Country of Operation:</strong> France</li>
              <li><strong>Contact Email:</strong> <a href="mailto:contact@chathera.com" className="text-blue-600 hover:underline">contact@chathera.com</a></li>
              <li><strong>Website:</strong> <a href="https://chathera.com" className="text-blue-600 hover:underline">https://chathera.com</a></li>
              <li><strong>Hosting Provider:</strong> [Insert hosting provider’s legal name and address]</li>
            </ul>
            <p>
              This Service is operated in compliance with French law and the General Data Protection Regulation (EU) 2016/679 ("GDPR").
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">2. Description of the Service</h2>
            <p>
              Chathera offers simulated relationships and conversations with AI-generated companions. These interactions are powered by artificial intelligence models (notably DeepSeek and OpenAI). The companions simulate emotional responses, but do not possess consciousness or free will.
            </p>
            <p>
              <strong>Important Disclaimer:</strong> The Service is not a medical, psychological, or therapeutic service. It is strictly recreational and should not be considered a substitute for professional advice.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">3. User Accounts</h2>
            <p>To access certain features, you must create an account. You agree to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Provide accurate and complete information;</li>
              <li>Maintain the confidentiality of your credentials;</li>
              <li>Notify us immediately of any unauthorized use.</li>
            </ul>
            <p>
              Chathera reserves the right to suspend or delete accounts that violate these条款.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">4. Use of the Service</h2>
            <p>You agree not to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Use the Service for unlawful purposes;</li>
              <li>Use the Service to harass, abuse, or harm others;</li>
              <li>Misrepresent your identity;</li>
              <li>Attempt to reverse engineer or disrupt our systems;</li>
              <li>Use the Service if you are under 18 years old.</li>
            </ul>
            <p>
              You are solely responsible for your use of the Service and interactions with AI companions. Please note that conversations may include explicit content if directed by the user.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">5. Payments and Subscriptions</h2>
            <p>
              Chathera uses Stripe for payment processing. By purchasing a subscription, you also agree to <a href="https://stripe.com/legal" className="text-blue-600 hover:underline">Stripe’s Terms of Use</a> and their <a href="https://stripe.com/privacy" className="text-blue-600 hover:underline">Privacy Policy</a>.
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>All payments are final. Refunds are not guaranteed unless required by law.</li>
              <li>You are responsible for managing your subscription (renewals, cancellations, updates).</li>
              <li>In case of fraud or payment issues, your account may be suspended without notice.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">6. AI Usage and Ethical Considerations</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>AI companions simulate emotions and affective engagement but are not real individuals.</li>
              <li>You may adjust the level of emotional interaction ("dependence") in your conversation settings.</li>
              <li>For your wellbeing, high levels of usage or emotional attachment may trigger automatic notifications suggesting support resources.</li>
              <li>You acknowledge that content generated by AI may be fictional, incorrect, or inappropriate.</li>
              <li>We disclaim all liability for decisions made based on AI-generated content.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">7. Data Collection and Protection</h2>
            <p>
              Our processing of your personal data complies with the GDPR. See our <a href="/privacy-policy" className="text-blue-600 hover:underline">Privacy Policy</a> for full details.
            </p>
            <p>As part of the service:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Your messages and interactions are stored internally.</li>
              <li>These messages are shared as prompts to DeepSeek for content generation.</li>
              <li>OpenAI is used for embedding and memory-related functionalities.</li>
              <li>Internal memory management is handled through Mem0 (not via external API) to enable conversation context, long-term memory, and interaction quality.</li>
            </ul>
            <p>You have the right to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Access, correct, delete, or port your data;</li>
              <li>Object to or restrict processing;</li>
              <li>Withdraw consent at any time;</li>
              <li>File a complaint with the CNIL (<a href="https://www.cnil.fr" className="text-blue-600 hover:underline">www.cnil.fr</a>).</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">8. International Data Transfers</h2>
            <p>
              Some of our providers (e.g., Stripe, OpenAI) are located outside the EU. Data transfers are protected through:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Standard Contractual Clauses (SCC), or</li>
              <li>The Data Privacy Framework.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">9. Intellectual Property</h2>
            <p>
              All content on the Service (texts, images, code, logos) is the exclusive property of Chathera or its licensors. You may not reproduce, distribute, or modify any part of the Service without written permission.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">10. Limitation of Liability</h2>
            <p>To the maximum extent permitted by law:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Chathera shall not be held liable for damages resulting from the use or inability to use the Service;</li>
              <li>We disclaim all liability for the accuracy, completeness, or usefulness of AI-generated content;</li>
              <li>The Service is provided "as is", without warranties of any kind.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">11. Termination</h2>
            <p>
              We may terminate or suspend access to the Service at our sole discretion, without prior notice, for any breach of these Terms. You may delete your account at any time via your account settings or by contacting us.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">12. Children's Privacy</h2>
            <p>
              Our Service is not intended for individuals under 18 years of age. We do not knowingly collect data from minors. Parents can contact us at <a href="mailto:contact@chathera.com" className="text-blue-600 hover:underline">contact@chathera.com</a> for immediate deletion.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">13. External Links</h2>
            <p>
              The Service may contain links to external websites. We are not responsible for the content, terms, or policies of third-party sites.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">14. Changes to the Terms</h2>
            <p>
              We may revise these Terms at any time. In case of substantial changes, we will notify you via email or a banner on the website. Your continued use of the Service after such modifications constitutes your agreement to the new Terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">15. Contact</h2>
            <p>
              If you have any questions or requests regarding these Terms, please contact us:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>By email: <a href="mailto:contact@chathera.com" className="text-blue-600 hover:underline">contact@chathera.com</a></li>
            </ul>
          </section>
        </div>
      </div>
    </main>
  );
}