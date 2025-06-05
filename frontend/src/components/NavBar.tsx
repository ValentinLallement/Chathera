import { Link } from "react-router-dom";
import Logo from "./Logo";

export default function NavBar() {
  return (
    <nav className="flex justify-center items-center absolute top-0 w-full backdrop-blur-3xl h-[68px] bg-[#000000]/5 z-50">
      <div className="text-white p-4 flex items-center h-[68px] w-[85%]  justify-between px-[12%] relative after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-full after:h-[1px] after:bg-gradient-to-r after:from-transparent after:via-white/20 after:to-transparent">
        <Link to="/" className="flex-shrink-0">
          <Logo />
        </Link>
        <ol className="flex space-x-4">
          <li>
            <Link
              to="/auth"
              className="group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none disabled:pointer-events-none disabled:opacity-50 "
            >
              Pricing
            </Link>
          </li>
          <li>
            <Link
              to="/demo"
              className="group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none disabled:pointer-events-none disabled:opacity-50 "
            >
              Demo
            </Link>
          </li>{" "}
          <li>
            <Link
              to="/profile"
              className="group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none disabled:pointer-events-none disabled:opacity-50 "
            >
              About
            </Link>
          </li>
          <li>
            <Link
              to="/profile"
              className="group inline-flex h-9 w-max items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none disabled:pointer-events-none disabled:opacity-50 "
            >
              Girls
            </Link>
          </li>
        </ol>
        <ol className="flex space-x-4 items-center">
          <li>
            <Link to="/auth">
              <button className="flex-shrink-0 whitespace-nowrap text-center rounded-lg border-white bg-white text-black text-sm font-medium py-1.5 px-3.5 cursor-pointer">
                Sign Up
              </button>
            </Link>
          </li>
          <li>
            <Link to="/contact">
              <button className="cursor-pointer relative flex-shrink-0 whitespace-nowrap text-center rounded-lg text-sm font-medium py-1.5 px-2">
                Try it for free
              </button>
            </Link>
          </li>
        </ol>
      </div>
    </nav>
  );
}
