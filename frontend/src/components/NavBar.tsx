import { Link } from "react-router-dom";

export default function NavBar() {
  return (
    <nav className="bg-gray-900 text-white p-4 flex-row justify-between">
      <ol className="flex space-x-4">
        <li>
          <Link to="/">Landing Page</Link>
        </li>
        <li>
          <Link to="/auth">Authentification</Link>
        </li>
        <li>
          <Link to="/profile">Profile</Link>
        </li>
      </ol>
    </nav>
  );
}
