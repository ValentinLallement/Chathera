import ChatHeraLogo from "../assets/images/StarLogo.webp";

export default function Logo() {
  return (
    <div className="flex items-center gap-2 ">
      <img
        src={ChatHeraLogo}
        alt="ChatHera Logo"
        className="w-5 h-5 object-cover"
      />
      <span className="text-xl font-bold text-white ">ChatHera</span>
    </div>
  );
}
