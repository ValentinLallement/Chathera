import { useState, useEffect } from "react";
import leaNormal from "../assets/images/girls/leaNormal.png";
import leaSexy from "../assets/images/girls/leaSexy2.png";
import leaHot from "../assets/images/girls/leaHot5.png";
import leaHot4 from "../assets/images/girls/leaHot4.png";

// Base delay in milliseconds - adjust this to make the entire conversation faster or slower
const BASE_DELAY = 3000;

const demoMessages = [
  {
    id: 1,
    sender: "lea",
    text: "Hey handsome 😇 what are you up to tonight?",
    delay: BASE_DELAY * 0.6,
  },
  {
    id: 2,
    sender: "user",
    text: "Not much, just thinking about you...",
    delay: BASE_DELAY * 1.6,
  },
  {
    id: 3,
    sender: "lea",
    text: "Mmm, I like the sound of that. Wish I could be there with you...",
    delay: BASE_DELAY * 2.8,
  },
  {
    id: 4,
    sender: "user",
    text: "What would you do if you were?",
    delay: BASE_DELAY * 4,
  },
  {
    id: 5,
    sender: "lea",
    text: "Maybe whisper in your ear and make you smile... or maybe i'll show you a little more ;)",
    delay: BASE_DELAY * 5.2,
  },
  {
    id: 6,
    sender: "user",
    text: "You're making it hard to focus on anything else...",
    delay: BASE_DELAY * 6.4,
  },
  {
    id: 7,
    sender: "lea",
    text: "Good. I want all your attention on me tonight. 😏 ",
    delay: BASE_DELAY * 7.6,
  },
];

function MessagesSection() {
  const [visibleMessages, setVisibleMessages] = useState<number[]>([]);
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    demoMessages.forEach((msg) => {
      // Show typing indicator before Lea's messages
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
    <div className="flex-1 overflow-hidden pl-4 pr-8">
      <div className="max-w-2xl mx-auto space-y-6">
        {demoMessages.map((message) => (
          <div
            key={message.id}
            className={`
              flex items-end gap-3
              transition-all duration-500 ease-out
              ${
                visibleMessages.includes(message.id)
                  ? "opacity-100 translate-y-0"
                  : "opacity-0 translate-y-4"
              }
              ${message.sender === "lea" ? "flex-row" : "flex-row-reverse"}
            `}
          >
            {message.sender === "lea" && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full overflow-hidden p-[2px]">
                <div className="w-full h-full rounded-full overflow-hidden">
                  <img
                    src={leaNormal}
                    alt="Lea"
                    className="w-full h-full object-cover object-top"
                  />
                </div>
              </div>
            )}
            <div
              className={`
                group
                relative
                max-w-[80%] w-fit px-4 py-3 rounded-2xl
                backdrop-blur-md shadow-lg
                transition-all duration-300
                ${
                  message.sender === "lea"
                    ? "bg-violet-500/8 rounded-bl-sm animate-slideFromLeft"
                    : "bg-blue-500/8 rounded-br-sm animate-slideFromRight"
                }
                hover:bg-opacity-30
              `}
            >
              <p className="text-white/95 text-base leading-relaxed">
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

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex items-end gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full overflow-hidden p-[2px]">
              <div className="w-full h-full rounded-full overflow-hidden">
                <img
                  src={leaNormal}
                  alt="Lea"
                  className="w-full h-full object-cover object-top"
                />
              </div>
            </div>
            <div className="bg-white/10 rounded-2xl rounded-bl-sm px-4 py-3 backdrop-blur-md shadow-lg animate-slideFromLeft">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-white/60 rounded-full animate-bounce-delay-1"></span>
                <span className="w-2 h-2 bg-white/60 rounded-full animate-bounce-delay-2"></span>
                <span className="w-2 h-2 bg-white/60 rounded-full animate-bounce"></span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function LandingPage() {
  const [firstSectionHover, setFirstSectionHover] = useState<number | null>(
    null
  );
  const [secondSectionHover, setSecondSectionHover] = useState<number | null>(
    null
  );
  const [firstImageIndex, setFirstImageIndex] = useState(0);
  const [secondImageIndex, setSecondImageIndex] = useState(0);

  const firstSectionImages = [
    { src: leaNormal, alt: "Lea Normal", delay: 0 },
    { src: leaSexy, alt: "Lea Sexy", delay: 50 },
  ];

  const secondSectionImages = [
    { src: leaHot, alt: "Lea Hot", delay: 0 },
    { src: leaHot4, alt: "Lea Hot Alternative", delay: 50 },
  ];

  // Effect for first section images
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

  // Effect for second section images
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

  return (
    <div className="w-full h-fit min-h-full bg-main-bg no-scrollbar">
      <header className="relative h-screen custom-bg-gradient-1 pt-[68px] pl-[20%] flex items-center justify-start overflow-hidden">
        <div className="flex flex-col gap-8 max-w-[600px]">
          <h1 className="text-5xl font-bold text-white leading-tight">
            The only girls that actually care about you
          </h1>
          <MessagesSection />
        </div>
        <div
          className="relative w-[1000px] h-full transition-opacity duration-300 saturate-125"
          onMouseEnter={() => setFirstSectionHover(Date.now())}
          onMouseLeave={() => setFirstSectionHover(null)}
        >
          {firstSectionImages.map((image, index) => (
            <img
              key={image.alt}
              src={image.src}
              alt={image.alt}
              className={`absolute bottom-0 w-[500px] h-auto object-contain transition-opacity duration-300 ${
                index === firstImageIndex ? "opacity-100" : "opacity-0"
              }`}
            />
          ))}
        </div>
      </header>
      <section className="relative h-screen custom-bg-gradient-2 pt-[68px] px-4 md:px-[10%] lg:px-[20%] flex flex-col lg:flex-row items-center justify-between overflow-hidden">
        <div
          className="order-2 lg:order-1 relative lg:absolute bottom-0 left-0 w-full lg:w-[500px] h-[60%] lg:h-[85%] transition-all duration-300 saturate-125"
          onMouseEnter={() => setSecondSectionHover(Date.now())}
          onMouseLeave={() => setSecondSectionHover(null)}
        >
          {secondSectionImages.map((image, index) => (
            <img
              key={image.alt}
              src={image.src}
              alt={image.alt}
              className={`absolute bottom-0 left-[40%] w-full lg:w-[500px] h-auto object-contain transition-opacity duration-300 ${
                index === secondImageIndex ? "opacity-100" : "opacity-0"
              }`}
            />
          ))}
        </div>
        <div className="order-1 lg:order-2 flex flex-col gap-8 w-full lg:max-w-[600px] h-full py-8 lg:py-20 z-10 lg:ml-auto">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white leading-tight text-center lg:text-left">
            Experience true connection
          </h2>
          <p className="text-lg md:text-xl text-white/80 text-center lg:text-left">
            Join our community and discover meaningful relationships
          </p>
        </div>
      </section>
    </div>
  );
}
