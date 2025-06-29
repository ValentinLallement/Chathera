import ChatHeraLogo from "../assets/images/StarLogo.webp";
import { useNavigate } from "react-router-dom";

interface LogoProps {
  isClickable?: boolean;
}

export default function Logo({ isClickable = true }: LogoProps) {
  const navigate = useNavigate();
  return (
    <div
      className={`flex items-center gap-2 cursor-pointer ${
        isClickable ? "hover:opacity-90" : ""
      }`}
      onClick={() => isClickable && navigate("/")}
    >
      <img
        src={ChatHeraLogo}
        alt="ChatHera Logo"
        className="w-5 h-5 object-cover"
      />
      <span className="text-xl font-bold text-white ">ChatHera</span>
    </div>
  );
}
