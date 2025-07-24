import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Mentions Légales | Chathera",
  description: "Consultez les mentions légales de Chathera pour en savoir plus sur l'éditeur du site, l'hébergement, et les conditions d'utilisation.",
};

export default function LegalMentionsPage() {
  return (
    <main className="min-h-screen px-6 md:px-12 py-32 bg-background text-foreground text-white">
      <div className="max-w-4xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold tracking-tight">Mentions Légales</h1>
        <p className="text-sm text-muted-foreground">
          Dernière mise à jour : 27 juin 2025
        </p>

        <div className="space-y-6 text-base leading-relaxed">
          <section>
            <p>
              Conformément à la loi n°2004-575 du 21 juin 2004 pour la confiance dans l'économie numérique (LCEN), il est précisé aux utilisateurs du site <a href="https://chathera.com" className="text-blue-600 hover:underline">https://chathera.com</a> l'identité des différents intervenants dans le cadre de sa réalisation et de son suivi.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">Éditeur du site</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Nom commercial :</strong> Chathera</li>
              <li><strong>Raison sociale :</strong> [Nom de la société ou nom de l’auto-entrepreneur]</li>
              <li><strong>Forme juridique :</strong> [SAS / SARL / Auto-entrepreneur / EI / EURL / autre]</li>
              <li><strong>Siège social :</strong> [Adresse complète avec code postal et ville]</li>
              <li><strong>Numéro SIRET / SIREN :</strong> [XXXXXXXXXXXXX]</li>
              <li><strong>Numéro RCS :</strong> [RCS + Ville d'immatriculation]</li>
              <li><strong>TVA intracommunautaire :</strong> [le cas échéant]</li>
              <li><strong>Directeur de la publication :</strong> [Nom, généralement le dirigeant légal]</li>
              <li><strong>Contact :</strong> <a href="mailto:contact@chathera.com" className="text-blue-600 hover:underline">contact@chathera.com</a></li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">Hébergement du site</h2>
            <p>Le site est hébergé par :</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Nom de l’hébergeur :</strong> [Ex : OVHcloud]</li>
              <li><strong>Adresse :</strong> [Adresse complète de l’hébergeur]</li>
              <li><strong>Téléphone :</strong> [Numéro]</li>
              <li><strong>Site internet :</strong> <a href="https://www.exemple.com" className="text-blue-600 hover:underline">https://www.exemple.com</a></li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">Conception et développement</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Responsable technique :</strong> [Ton nom ou société de développement]</li>
              <li><strong>Contact technique :</strong> [Adresse email technique ou formulaire de contact]</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">Conditions d’utilisation</h2>
            <p>
              L’utilisation du site implique l’acceptation pleine et entière des <a href="/terms-of-service" className="text-blue-600 hover:underline">Conditions Générales d’Utilisation (CGU)</a> et de la <a href="/privacy-policy" className="text-blue-600 hover:underline">Politique de confidentialité</a>.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">Propriété intellectuelle</h2>
            <p>
              Le site Chathera et tous les éléments qui le composent (logos, textes, images, contenus, interfaces) sont la propriété exclusive de Chathera ou de ses partenaires. Toute reproduction ou représentation sans autorisation préalable est interdite.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">Liens hypertextes et cookies</h2>
            <p>
              Le site peut contenir des liens vers d’autres sites. Chathera décline toute responsabilité concernant le contenu de ces sites externes.
            </p>
            <p>
              La navigation sur le site peut entraîner l’installation de cookies. Pour en savoir plus, consultez notre <a href="/cookies-policy" className="text-blue-600 hover:underline">Politique de Cookies</a>.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">Données personnelles</h2>
            <p>
              Chathera s'engage à respecter la réglementation applicable à la protection des données à caractère personnel, notamment le RGPD. Pour plus d’informations, voir notre <a href="/privacy-policy" className="text-blue-600 hover:underline">Politique de confidentialité</a>.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mt-6 mb-4">Droit applicable et juridiction compétente</h2>
            <p>
              Les présentes mentions légales sont régies par le droit français. En cas de litige, les tribunaux compétents seront ceux du ressort de la Cour d’appel de [ville].
            </p>
          </section>
        </div>
      </div>
    </main>
  );
}