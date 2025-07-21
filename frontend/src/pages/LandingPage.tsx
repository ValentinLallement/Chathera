import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import type { MouseEvent } from "react";
import leaNormal from "../assets/images/girls/leaNormal.png";
import leaSexy from "../assets/images/girls/leaSexy2.png";
import leaHot from "../assets/images/girls/leaHot3.png";
import leaHot4 from "../assets/images/girls/leaHot4.png";
import leaUltra from "../assets/images/girls/leaUltra.png";
import leaSupra from "../assets/images/girls/leaSupra.png";
import Title from "../components/Title";

const BASE_DELAY = 2000; // Increased from 3000

const demoMessages = [
  {
    id: 1,
    sender: "lea",
    text: "Hey handsome 😇 what are you up to tonight?",
    delay: BASE_DELAY * 0.8, // Adjusted multipliers for smoother pacing
  },
  {
    id: 2,
    sender: "user",
    text: "Not much, just thinking about you...",
    delay: BASE_DELAY * 2,
  },
  {
    id: 3,
    sender: "lea",
    text: "Mmm, I like the sound of that. Wish I could be there with you...",
    delay: BASE_DELAY * 3.2,
  },
  {
    id: 4,
    sender: "user",
    text: "What would you do if you were?",
    delay: BASE_DELAY * 4.4,
  },
  {
    id: 5,
    sender: "lea",
    text: "Maybe whisper in your ear and make you smile... or maybe i'll show you a little more ;)",
    delay: BASE_DELAY * 5.6,
  },
  {
    id: 6,
    sender: "user",
    text: "You're making it hard to focus on anything else...",
    delay: BASE_DELAY * 6.8,
  },
  {
    id: 7,
    sender: "lea",
    text: "Good. I want all your attention on me tonight. 😏 ",
    delay: BASE_DELAY * 8,
  },
];

function MessagesSection() {
  const [visibleMessages, setVisibleMessages] = useState<number[]>([]);
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    demoMessages.forEach((msg) => {
      if (msg.sender === "lea") {
        setTimeout(() => {
          setIsTyping(true);
        }, msg.delay - 1000);
      }

      setTimeout(() => {
        setIsTyping(false);
        setVisibleMessages((prev) => [...prev, msg.id]);
      }, msg.delay);
    });
  }, []);

  return (
    <>
      <Title>Welcome to Chathera</Title>
      <div className="flex-1 overflow-hidden px-4 lg:pr-8">
        <div className="max-w-2xl mx-auto space-y-4 lg:space-y-6">
          {demoMessages.map((message, index) => (
            <div
              key={message.id}
              style={{
                transitionDelay: `${index * 100}ms`,
              }}
              className={`
              flex items-end gap-2 lg:gap-3
              transition-all duration-700 ease-out
              ${
                visibleMessages.includes(message.id)
                  ? "opacity-100 translate-y-0"
                  : "opacity-0 translate-y-4"
              }
              ${message.sender === "lea" ? "flex-row" : "flex-row-reverse"}
            `}
            >
              {message.sender === "lea" && (
                <div className="flex-shrink-0 w-6 h-6 lg:w-8 lg:h-8 rounded-full overflow-hidden p-[2px] transition-transform duration-300 ease-out transform hover:scale-110">
                  <div className="w-full h-full rounded-full overflow-hidden">
                    <img
                      src={leaNormal}
                      alt="Lea"
                      className="w-full h-full object-cover object-top transition-transform duration-300 ease-out hover:scale-105"
                    />
                  </div>
                </div>
              )}
              <div
                className={`
                group
                relative
                max-w-[85%] sm:max-w-[80%] w-fit px-3 py-2 lg:px-4 lg:py-3 rounded-2xl
                backdrop-blur-xl shadow-lg
                transition-all duration-500 ease-out
                text-sm lg:text-base
                animate-floatIn message-shimmer
                ${
                  message.sender === "lea"
                    ? "bg-gradient-to-br from-violet-500/10 to-fuchsia-500/10 rounded-bl-sm animate-slideFromLeft border border-violet-500/10"
                    : "bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-br-sm animate-slideFromRight border border-blue-500/10"
                }
                hover:shadow-xl hover:scale-[1.02] hover:border-opacity-50
              `}
              >
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-white/[0.02] to-transparent opacity-50 transition-opacity group-hover:opacity-75" />
                <div className="absolute -inset-0.5 rounded-2xl bg-gradient-to-r from-violet-500/20 to-fuchsia-500/20 opacity-0 blur transition group-hover:opacity-100 animate-pulse" />

                <p className="text-white/95 text-base leading-relaxed relative z-10 text-left">
                  {message.text}
                </p>
                <div
                  className={`
                  absolute -bottom-5 ${
                    message.sender === "lea" ? "left-0" : "right-0"
                  }
                  text-xs text-white/40 opacity-0 group-hover:opacity-100 transition-opacity
                `}
                >
                  {new Date().toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex items-end gap-2 lg:gap-3">
              <div className="flex-shrink-0 w-6 h-6 lg:w-8 lg:h-8 rounded-full overflow-hidden p-[2px] transition-transform duration-300 ease-out transform hover:scale-110">
                <div className="w-full h-full rounded-full overflow-hidden">
                  <img
                    src={leaNormal}
                    alt="Lea"
                    className="w-full h-full object-cover object-top transition-transform duration-300 ease-out hover:scale-105"
                  />
                </div>
              </div>
              <div className="bg-gradient-to-br from-violet-500/10 to-fuchsia-500/10 rounded-2xl rounded-bl-sm px-3 py-2 lg:px-4 lg:py-3 backdrop-blur-xl shadow-lg animate-floatIn border border-violet-500/10 group">
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-white/[0.02] to-transparent opacity-50" />
                <div className="absolute -inset-0.5 rounded-2xl bg-gradient-to-r from-violet-500/20 to-fuchsia-500/20 opacity-0 blur transition group-hover:opacity-100" />
                <div className="flex gap-1.5 relative z-10">
                  <span className="w-1.5 h-1.5 lg:w-2 lg:h-2 bg-violet-400/60 rounded-full animate-bounce-delay-1"></span>
                  <span className="w-1.5 h-1.5 lg:w-2 lg:h-2 bg-violet-400/60 rounded-full animate-bounce-delay-2"></span>
                  <span className="w-1.5 h-1.5 lg:w-2 lg:h-2 bg-violet-400/60 rounded-full animate-bounce"></span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
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

export default function LandingPage() {
  const navigate = useNavigate();
  const [firstSectionHover, setFirstSectionHover] = useState<number | null>(
    null
  );
  const [secondSectionHover, setSecondSectionHover] = useState<number | null>(
    null
  );
  const [thirdSectionHover, setThirdSectionHover] = useState<number | null>(
    null
  );
  const [firstImageIndex, setFirstImageIndex] = useState(0);
  const [secondImageIndex, setSecondImageIndex] = useState(0);
  const [thirdImageIndex, setThirdImageIndex] = useState(0);

  const firstSectionImages = [
    { src: leaNormal, alt: "Lea Normal", delay: 0 },
    { src: leaSexy, alt: "Lea Sexy", delay: 50 },
  ];

  const secondSectionImages = [
    { src: leaHot, alt: "Lea Hot", delay: 0 },
    { src: leaHot4, alt: "Lea Hot Alternative", delay: 50 },
  ];

  const thirdSectionImages = [
    { src: leaUltra, alt: "Lea Ultra", delay: 0 },
    { src: leaSupra, alt: "Lea Supra", delay: 50 },
  ];

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    if (firstSectionHover !== null) {
      const checkTransition = () => {
        const hoverDuration = Date.now() - firstSectionHover;
        const nextIndex = firstSectionImages.findIndex(
          (img) => hoverDuration < img.delay
        );
        const newIndex =
          nextIndex === -1 ? firstSectionImages.length - 1 : nextIndex - 1;

        if (newIndex !== firstImageIndex) {
          setFirstImageIndex(newIndex);
        }

        if (newIndex < firstSectionImages.length - 1) {
          timeoutId = setTimeout(checkTransition, 50);
        }
      };

      checkTransition();
    } else {
      setFirstImageIndex(0);
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [firstSectionHover, firstImageIndex]);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    if (secondSectionHover !== null) {
      const checkTransition = () => {
        const hoverDuration = Date.now() - secondSectionHover;
        const nextIndex = secondSectionImages.findIndex(
          (img) => hoverDuration < img.delay
        );
        const newIndex =
          nextIndex === -1 ? secondSectionImages.length - 1 : nextIndex - 1;

        if (newIndex !== secondImageIndex) {
          setSecondImageIndex(newIndex);
        }

        if (newIndex < secondSectionImages.length - 1) {
          timeoutId = setTimeout(checkTransition, 50);
        }
      };

      checkTransition();
    } else {
      setSecondImageIndex(0);
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [secondSectionHover, secondImageIndex]);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    if (thirdSectionHover !== null) {
      const checkTransition = () => {
        const hoverDuration = Date.now() - thirdSectionHover;
        const nextIndex = thirdSectionImages.findIndex(
          (img) => hoverDuration < img.delay
        );
        const newIndex =
          nextIndex === -1 ? thirdSectionImages.length - 1 : nextIndex - 1;

        if (newIndex !== thirdImageIndex) {
          setThirdImageIndex(newIndex);
        }

        if (newIndex < thirdSectionImages.length - 1) {
          timeoutId = setTimeout(checkTransition, 50);
        }
      };

      checkTransition();
    } else {
      setThirdImageIndex(0);
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [thirdSectionHover, thirdImageIndex]);

  return (
    <div className="w-full h-fit min-h-full bg-main-bg no-scrollbar">
      <header className="relative custom-bg-gradient-1 pt-[20px]  min-h-[1556px] lg:min-h-screen px-4 md:pl-[10%] lg:pl-[20%] flex flex-col lg:flex-row items-start justify-start overflow-hidden">
        <div className="flex flex-col gap-8 w-full lg:max-w-[600px] z-20 text-center lg:text-left mt-8 lg:mt-[15vh]">
          <h1 className="text-4xl md:text-5xl font-bold text-white leading-tight">
            The only girls that actually care about you
          </h1>
          <MessagesSection />
        </div>
        <div
          className="absolute right-0 bottom-0 w-full md:w-[600px] lg:w-[700px] h-[90vh] transition-opacity duration-300 saturate-125 z-10"
          onMouseEnter={() => setFirstSectionHover(Date.now())}
          onMouseLeave={() => setFirstSectionHover(null)}
        >
          {firstSectionImages.map((image, index) => (
            <img
              key={image.alt}
              src={image.src}
              alt={image.alt}
              className={`absolute bottom-0 left-1/2 lg:left-auto lg:right-[40%] transform -translate-x-1/2 lg:translate-x-0 h-full w-auto object-contain object-bottom transition-opacity duration-300 ${
                index === firstImageIndex ? "opacity-100" : "opacity-0"
              }`}
            />
          ))}
        </div>
      </header>

      <section className="relative min-h-[1452px] lg:min-h-screen custom-bg-gradient-2 pt-[68px] px-4 md:px-[10%] lg:px-[20%] flex flex-col lg:flex-row items-start justify-start overflow-hidden">
        <div
          className="absolute left-0 bottom-0 w-full md:w-[600px] lg:w-[700px] h-[90vh] transition-opacity duration-300 saturate-125 z-10"
          onMouseEnter={() => setSecondSectionHover(Date.now())}
          onMouseLeave={() => setSecondSectionHover(null)}
        >
          {secondSectionImages.map((image, index) => (
            <img
              key={image.alt}
              src={image.src}
              alt={image.alt}
              className={`absolute bottom-0 left-1/2 lg:left-[40%] transform -translate-x-1/2 lg:translate-x-0 h-full w-auto object-contain object-bottom transition-opacity duration-300 hover:saturate-160 ${
                index === secondImageIndex ? "opacity-100" : "opacity-0"
              }`}
            />
          ))}
        </div>
        <div className="order-1 lg:order-2 flex flex-col gap-6 lg:gap-8 w-full lg:max-w-[600px] z-20 lg:ml-auto mt-8 lg:mt-[15vh]">
          <div className="space-y-3">
            <div className="w-full flex justify-center lg:justify-start">
              <span className="inline-block px-3 py-1 rounded-full text-xs font-medium bg-violet-500/20 text-violet-400 border border-violet-500/20">
                Advanced Features
              </span>
            </div>
            <h2 className="text-3xl pt-4 md:text-4xl lg:text-5xl font-bold text-white leading-tight text-center lg:text-left ">
              Experience True Connection
            </h2>
            <p className="text-base lg:text-lg text-white/80 text-center lg:text-left max-w-xl mx-auto lg:mx-0">
              Discover a new level of companionship with our advanced AI
              personalities. Engage in meaningful conversations that go beyond
              small talk.
            </p>
          </div>
          <ul className="space-y-3 text-white/70 max-w-xl mx-auto lg:mx-0">
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400"></span>
              Deep personality customization
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400"></span>
              Memory retention & context awareness
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400"></span>
              Natural conversation flow
            </li>
          </ul>
          <div className="flex flex-col sm:flex-row gap-4 mt-4 justify-center lg:justify-start">
            <button className="px-6 py-2.5 rounded-lg bg-violet-500/20 text-violet-400 border border-violet-500/20 hover:bg-violet-500/30 transition-colors w-full sm:w-auto">
              Try for Free
            </button>
            <button className="px-6 py-2.5 rounded-lg bg-transparent text-white/80 border border-white/20 hover:bg-white/5 transition-colors w-full sm:w-auto">
              Learn More
            </button>
          </div>
        </div>
      </section>

      <section className="relative min-h-[1460px] lg:min-h-screen custom-bg-gradient-2 pt-[68px] px-4 md:px-[10%] lg:px-[20%] flex flex-col lg:flex-row items-center justify-between overflow-hidden">
        <div
          className="absolute right-0 bottom-0 w-full lg:w-[700px] h-[60vh] lg:h-[90%] transition-all duration-300 saturate-125"
          onMouseEnter={() => setThirdSectionHover(Date.now())}
          onMouseLeave={() => setThirdSectionHover(null)}
        >
          {thirdSectionImages.map((image, index) => (
            <img
              key={image.alt}
              src={image.src}
              alt={image.alt}
              className={`absolute bottom-0 left-1/2 lg:left-auto lg:right-[40%] transform -translate-x-1/2 lg:translate-x-0 w-[80%] lg:w-[550px] h-auto object-contain transition-opacity duration-300 ${
                index === thirdImageIndex ? "opacity-100" : "opacity-0"
              }`}
            />
          ))}
          <div className="absolute bottom-[15%] right-[40%] w-32 h-32 bg-pink-500/30 rounded-full blur-[100px]" />
          <div className="absolute top-[25%] left-[40%] w-32 h-32 bg-purple-500/30 rounded-full blur-[100px]" />
        </div>
        <div className="order-2 lg:order-1 flex flex-col gap-8 w-full lg:max-w-[600px] h-full py-8 lg:py-20 z-10">
          <div className="space-y-4">
            <div className="gap-2 w-full flex justify-center lg:justify-start">
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-pink-500/20 text-pink-400 border border-pink-500/20">
                Premium Access
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-500/20 text-purple-400 border border-purple-500/20">
                NSFW Enabled
              </span>
            </div>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold leading-tight text-center lg:text-left bg-gradient-to-r from-pink-500 to-violet-500 bg-clip-text text-transparent">
              Unlock Intimate Experiences
            </h2>
            <p className="text-lg md:text-xl text-white/80 text-center lg:text-left">
              Experience deeper connections with exclusive NSFW content and
              unrestricted conversations. Your desires, explored safely and
              privately.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
            {[
              {
                title: "Unrestricted Access",
                description:
                  "Full access to NSFW content and intimate conversations",
              },
              {
                title: "Enhanced Privacy",
                description: "End-to-end encryption for complete discretion",
              },
              {
                title: "Custom Scenarios",
                description:
                  "Create and explore personalized intimate scenarios",
              },
              {
                title: "Priority Support",
                description: "24/7 dedicated support for premium members",
              },
            ].map((feature) => (
              <SpotlightItem key={feature.title}>
                <div
                  className="feature-card p-4 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 group"
                  onMouseMove={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    e.currentTarget.style.setProperty("--x", `${x}px`);
                    e.currentTarget.style.setProperty("--y", `${y}px`);
                  }}
                >
                  <h3 className="text-white/90 font-semibold mb-2 relative z-10">
                    {feature.title}
                  </h3>
                  <p className="text-white/70 text-sm relative z-10">
                    {feature.description}
                  </p>
                </div>
              </SpotlightItem>
            ))}

          </div>

          <div className="flex flex-col sm:flex-row gap-4 mt-6 w-full justify-center ">
            <button
                onClick={() => navigate("/pricing")}
                className="group relative px-6 py-3 rounded-lg overflow-hidden transition-all duration-300 glow-effect"
              >
              <div className="absolute inset-0 bg-gradient-to-r from-pink-500/20 to-violet-500/20 backdrop-blur-md" />
              <div className="absolute inset-0 bg-gradient-to-r from-pink-500 to-violet-500 opacity-0 group-hover:opacity-20 transition-opacity duration-700" />
              <div className="absolute inset-[1px] rounded-lg bg-black/40 backdrop-blur-xl" />

              <div
                className="absolute inset-0 bg-gradient-to-r from-pink-500 to-violet-500 opacity-30"
                style={{
                  backgroundSize: "200% 200%",
                  animation: "shine 8s linear infinite",
                }}
              />
              <div className="absolute inset-[1px] rounded-lg bg-black/50" />

              <span className="cursor-pointer relative z-10 font-medium bg-gradient-to-r from-pink-400 to-violet-400 bg-clip-text text-transparent">
                Upgrade Now
              </span>
            </button>
            <SpotlightItem>
              <button className="cursor-pointer px-6 py-3 rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 text-white/90 hover:bg-white/10 transition-colors">
                View Plans
              </button>
            </SpotlightItem>
          </div>
        </div>
      </section>
    </div>
  );
}
