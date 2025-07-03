import { Outlet, Link, useLocation } from "react-router-dom";
import { useSidebarStore } from "../stores/sidebarStore";
import { useAuthStore } from "../stores/authStore";
import { useGetSubscriptionInfos } from "../hooks/useApi";
import Logo from "../components/Logo";
import type { MouseEvent } from "react";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faVenusMars,
  faCrown,
  faInfinity,
} from "@fortawesome/free-solid-svg-icons";

// Import SVG icons
import Bar_Left from "../assets/images/svgs/Bar_Left.svg";
import HomeIcon from "../assets/images/svgs/Home.svg";
import ChatIcon from "../assets/images/svgs/Chat.svg";
//import GirlIcon from "../assets/images/svgs/Girl.svg";
import SettingsIcon from "../assets/images/svgs/Settings.svg";

interface MenuItemProps {
  to: string;
  icon: string | React.ReactNode;
  text: string;
  isActive?: boolean;
}

const SpotlightItem = ({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    e.currentTarget.style.setProperty("--x", `${x}px`);
    e.currentTarget.style.setProperty("--y", `${y}px`);
  };

  return (
    <div
      className={`cursor-spotlight ${className}`}
      onMouseMove={handleMouseMove}
      onMouseLeave={(e) => {
        e.currentTarget.style.setProperty("--x", "50%");
        e.currentTarget.style.setProperty("--y", "50%");
      }}
    >
      {children}
    </div>
  );
};

const MenuItem = ({ to, icon, text, isActive }: MenuItemProps) => {
  return (
    <Link to={to}>
      <SpotlightItem
        className={`group flex items-center gap-3 px-3 py-2 rounded-xl transition-all duration-300
        ${
          isActive
            ? "bg-violet-500/20 border border-violet-500/20"
            : "hover:bg-white/5 border border-transparent hover:border-white/10"
        }`}
      >
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center bg-black/20 backdrop-blur-xl border border-white/5 transition-all duration-300 
          ${isActive ? "border-violet-500/20" : "group-hover:border-white/10"}`}
        >
          {typeof icon === "string" ? (
            <img
              src={icon}
              alt={text}
              className={`w-6 h-6 transition-transform duration-300 ${
                isActive ? "transform scale-110" : "group-hover:scale-105"
              }`}
            />
          ) : (
            icon
          )}
        </div>
        <span
          className={`text-sm font-medium transition-colors duration-300 
          ${
            isActive
              ? "text-violet-400"
              : "text-white/70 group-hover:text-white"
          }`}
        >
          {text}
        </span>
      </SpotlightItem>
    </Link>
  );
};

export default function HomePage() {
  const { isOpen, toggle } = useSidebarStore();
  const { user } = useAuthStore();
  const location = useLocation();
  const { data: subscriptionData } = useGetSubscriptionInfos();

  const renderUpgradeWidget = () => {
    const plan = subscriptionData?.subscriptions?.plan?.toLowerCase() || "free";

    if (plan === "premium") {
      return (
        <SpotlightItem className="p-4 rounded-xl bg-gradient-to-r from-yellow-500/10 to-yellow-400/5 backdrop-blur-sm border border-yellow-500/10">
          <div className="flex items-center gap-2 mb-2">
            <FontAwesomeIcon icon={faCrown} className="text-yellow-400" />
            <h4 className="text-sm font-medium text-white">Premium Plan</h4>
          </div>
          <p className="text-xs text-white/70 mb-3">
            {subscriptionData?.subscriptions?.message_count} / 600 messages used
            this month
          </p>
          <Link to="/dashboard/settings">
            <button className="w-full px-4 py-2 rounded-lg bg-yellow-500/20 text-yellow-400 text-sm font-medium border border-yellow-500/20 hover:bg-yellow-500/30 transition-colors">
              Manage Subscription
            </button>
          </Link>
        </SpotlightItem>
      );
    } else if (plan === "payg") {
      return (
        <SpotlightItem className="p-4 rounded-xl bg-gradient-to-r from-violet-500/10 to-violet-400/5 backdrop-blur-sm border border-violet-500/10">
          <div className="flex items-center gap-2 mb-2">
            <FontAwesomeIcon icon={faInfinity} className="text-violet-400" />
            <h4 className="text-sm font-medium text-white">Full Access Plan</h4>
          </div>
          <p className="text-xs text-white/70 mb-3">
            {subscriptionData?.subscriptions?.message_count} messages this month
          </p>
          <Link to="/dashboard/settings">
            <button className="w-full px-4 py-2 rounded-lg bg-violet-500/20 text-violet-400 text-sm font-medium border border-violet-500/20 hover:bg-emerald-500/30 transition-colors">
              Manage Subscription
            </button>
          </Link>
        </SpotlightItem>
      );
    }

    return (
      <SpotlightItem className="p-4 rounded-xl bg-gradient-to-r from-emerald-500/10 to-emerald-400/5 backdrop-blur-sm border border-emerald-500/10">
        <h4 className="text-sm font-medium text-white mb-2">
          Upgrade to Premium
        </h4>
        <p className="text-xs text-white/70 mb-3">
          {subscriptionData?.subscriptions?.message_count || 0} / 10 messages
          used this month
        </p>
        <Link to="/pricing">
          <button className="w-full px-4 py-2 rounded-lg bg-emerald-500/20 text-emerald-400 text-sm font-medium border border-emerald-500/20 hover:bg-violet-500/30 transition-colors">
            Upgrade Now
          </button>
        </Link>
      </SpotlightItem>
    );
  };

  return (
    <div className="p-[20px] w-screen h-screen bg-gradient-to-b from-[#1f1f1f] to-[#000000] flex flex-row">
      {/* Sidebar - fully hidden when collapsed */}
      <div
        className={`h-full text-white transition-all duration-300 ease-in-out ${
          isOpen
            ? "w-[320px] opacity-100 visible p-4 pt-7 mr-5 rounded-3xl"
            : "w-0 opacity-0 invisible p-0"
        }`}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between mb-8">
            <div
              className={`transition-opacity duration-300 pl-5 ${
                isOpen ? "opacity-100" : "opacity-0"
              }`}
            >
              <Logo />
            </div>
            <button
              onClick={toggle}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
              aria-label={isOpen ? "Collapse sidebar" : "Expand sidebar"}
            >
              <img
                src={Bar_Left}
                alt="Toggle sidebar"
                className="w-6 h-6 transition-transform duration-300 text-white [&>path]:stroke-white cursor-pointer"
              />
            </button>
          </div>

          {/* Menu Items */}
          <div className="flex flex-col gap-2">
            <MenuItem
              to="/dashboard"
              icon={HomeIcon}
              text="Home"
              isActive={location.pathname === "/dashboard"}
            />
            <MenuItem
              to="/dashboard/chat"
              icon={ChatIcon}
              text="Messages"
              isActive={location.pathname.includes("/chat")}
            />
            <MenuItem
              to="/dashboard/partners"
              icon={<FontAwesomeIcon icon={faVenusMars} />}
              text="Partners"
              isActive={location.pathname.includes("/partners")}
            />
            <MenuItem
              to="/dashboard/settings"
              icon={SettingsIcon}
              text="Settings"
              isActive={location.pathname.includes("/settings")}
            />
          </div>

          {/* Bottom section */}
          <div className="mt-auto">
            {renderUpgradeWidget()}

            <SpotlightItem className="p-4 rounded-xl bg-gradient-to-r from-gray-500/11 to-gray-400/5 backdrop-blur-sm border border-gray-500/10 mt-4 flex justify-between items-center">
              <div>
                <p className="text-white/90 font-medium">
                  {user?.name || "Guest"}
                </p>
                <p className="text-white/30 text-sm mt-0.5">{user?.username}</p>
              </div>
              <div
                className={`px-3 py-1 rounded-xl bg-gradient-to-b ${
                  subscriptionData?.subscriptions?.plan?.toLowerCase() ===
                  "premium"
                    ? "from-yellow-500/22 to-yellow-400/15 border-yellow-500/15"
                    : subscriptionData?.subscriptions?.plan?.toLowerCase() ===
                      "payg"
                    ? "from-violet-500/22 to-violet-400/15 border-violet-500/15"
                    : "from-emerald-500/22 to-emerald-400/15 border-emerald-500/15"
                } backdrop-blur-sm border flex justify-between items-center`}
              >
                <p className="text-sm text-white/80 font-medium capitalize">
                  {subscriptionData?.subscriptions?.plan?.toLowerCase() ==
                  "payg"
                    ? "Unlimited"
                    : subscriptionData?.subscriptions?.plan || "Free"}
                </p>
              </div>
            </SpotlightItem>
          </div>
        </div>
      </div>

      <div className="flex-1 relative">
        {!isOpen && (
          <button
            onClick={toggle}
            className="absolute cursor-pointer top-6 left-6 z-50 p-2 rounded-lg bg-black/40 hover:bg-black/60 backdrop-blur-xl border border-white/10 text-white transition-all duration-300 ease-in-out"
            aria-label="Expand sidebar"
          >
            <img
              src={Bar_Left}
              alt="Toggle sidebar"
              className="w-6 h-6 text-white [&>path]:stroke-white"
            />
          </button>
        )}

        <Outlet />
      </div>
    </div>
  );
}
