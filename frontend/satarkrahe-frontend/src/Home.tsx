import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

const BRAND = "SatarkRahe.ai";
const tunnelLayers = Array.from({ length: 16 }, (_, index) => index);

type Stage = "idle" | "outline" | "compress" | "tunnel" | "done";

type BrandTextProps = {
  stage: Stage;
  onActivate: () => void;
};

function BrandText({ stage, onActivate }: BrandTextProps) {
  const isIdle = stage === "idle";
  const isOutline = stage === "outline";
  const isCompress = stage === "compress";

  return (
    <motion.button
      type="button"
      aria-label="Initialize SatarkRahe.ai"
      disabled={!isIdle}
      onClick={onActivate}
      className="relative grid w-[min(92vw,980px)] cursor-pointer place-items-center border-0 bg-transparent p-0 text-center outline-none disabled:cursor-default"
      animate={
        isCompress
          ? {
              scaleX: [1, 0.42, 0.18],
              scaleY: [1, 1.08, 1.18],
              opacity: [1, 0.96, 0],
            }
          : { scaleX: 1, scaleY: 1, opacity: 1 }
      }
      whileHover={
        isIdle
          ? {
              scale: 1.05,
              textShadow:
                "0 0 4px rgba(246,236,172,0.95), 0 0 10px rgba(184,18,2,0.9)",
            }
          : undefined
      }
      whileTap={isIdle ? { scale: 0.985 } : undefined}
      transition={
        isCompress
          ? { type: "spring", stiffness: 230, damping: 18, mass: 0.7 }
          : { type: "spring", stiffness: 170, damping: 18 }
      }
    >
      <motion.h1
        className="absolute z-10 whitespace-nowrap bg-gradient-to-r from-[#b81202] via-[#f6ecac] to-[#b81202] bg-clip-text text-5xl font-black tracking-tight text-transparent sm:text-6xl lg:text-7xl"
        style={{
          textShadow:
            "0 0 2px rgba(246,236,172,0.75), 0 0 8px rgba(184,18,2,0.72)",
        }}
        animate={{ opacity: isOutline || isCompress ? 0 : 1 }}
        transition={{ duration: 0.45, ease: "easeInOut" }}
      >
        {BRAND}
      </motion.h1>

      <svg
        viewBox="0 0 1200 220"
        role="img"
        aria-label={BRAND}
        className="relative z-20 h-auto w-full overflow-visible"
      >
        <defs>
          <clipPath id="satarkrahe-outline-reveal">
            <motion.rect
              x="0"
              y="0"
              width="1200"
              initial={{ height: 0 }}
              animate={{ height: isOutline || isCompress ? 220 : 0 }}
              transition={{ duration: 1.45, ease: "easeInOut" }}
            />
          </clipPath>
        </defs>

        <motion.text
          x="600"
          y="128"
          textAnchor="middle"
          dominantBaseline="middle"
          fill="transparent"
          stroke="#f6ecac"
          strokeWidth="2.2"
          strokeLinecap="square"
          strokeLinejoin="miter"
          clipPath="url(#satarkrahe-outline-reveal)"
          className="select-none text-[128px] font-black tracking-tight"
          style={{
            fontFamily:
              "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            paintOrder: "stroke",
            filter:
              "drop-shadow(0 0 2px rgba(246,236,172,0.95)) drop-shadow(0 0 7px rgba(184,18,2,0.85))",
          }}
          animate={{ opacity: isOutline || isCompress ? 1 : 0 }}
          transition={{ duration: 0.35, ease: "easeInOut" }}
        >
          {BRAND}
        </motion.text>
      </svg>
    </motion.button>
  );
}

function Tunnel() {
  const duration = 2.8;
  const activeLayers = tunnelLayers.slice(0, 7);
  const totalLayers = activeLayers.length;

  return (
    <motion.div
      className="absolute inset-0 z-30 flex items-center justify-center overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.45, ease: "easeInOut" }}
    >
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(circle at center, rgba(246,236,172,0.12) 0%, rgba(184,18,2,0.12) 22%, rgba(0,0,0,0) 52%)",
        }}
      />

      <div
        className="relative h-[min(78vw,680px)] w-[min(78vw,680px)]"
        style={{ perspective: 1000, transformStyle: "preserve-3d" }}
      >
        {activeLayers.map((layer, index) => {
          const delay = (index / totalLayers) * duration;

          return (
            <motion.div
              key={layer}
              className="absolute left-1/2 top-1/2 aspect-square border border-solid border-[#f6ecac]"
              style={{
                width: "34%",
                boxShadow: "0 0 6px #f6ecac, 0 0 16px #b81202",
                transformStyle: "preserve-3d",
              }}
              initial={{
                x: "-50%",
                y: "-50%",
                rotate: 45,
                scale: 0.5,
                opacity: 0,
              }}
              animate={{
                scale: [0.5, 3.5],
                opacity: [0.6, 0.38, 0],
                rotate: 45,
                z: [-180, 420],
              }}
              transition={{
                duration,
                delay,
                ease: "linear",
                repeat: Infinity,
                repeatDelay: 0,
              }}
            />
          );
        })}
      </div>

      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(circle at center, transparent 0%, transparent 34%, rgba(0,0,0,0.24) 62%, rgba(0,0,0,0.78) 100%)",
        }}
      />
    </motion.div>
  );
}

export default function Home() {
  const [stage, setStage] = useState<Stage>("idle");
  const timers = useRef<number[]>([]);

  useEffect(() => {
    return () => {
      timers.current.forEach(window.clearTimeout);
    };
  }, []);

  const start = () => {
    if (stage !== "idle") return;

    setStage("outline");
    timers.current = [
      window.setTimeout(() => setStage("compress"), 1600),
      window.setTimeout(() => setStage("tunnel"), 2600),
      window.setTimeout(() => setStage("done"), 5200),
    ];
  };

  return (
    <main className="relative flex h-screen w-screen items-center justify-center overflow-hidden bg-black text-white">
      <motion.div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(circle at center, rgba(184,18,2,0.28) 0%, rgba(85,13,8,0.14) 28%, rgba(0,0,0,0.96) 64%, #000 100%)",
        }}
        animate={{ opacity: [0.86, 1, 0.86], scale: [1, 1.04, 1] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />

      <motion.div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage:
            "linear-gradient(rgba(246,236,172,0.24) 1px, transparent 1px), linear-gradient(90deg, rgba(246,236,172,0.18) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
        }}
        animate={{ x: [0, -12, 0], y: [0, 12, 0] }}
        transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
      />

      <AnimatePresence mode="wait">
        {stage !== "tunnel" && stage !== "done" && (
          <motion.div
            key="brand"
            className="relative z-20 grid place-items-center"
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            <BrandText stage={stage} onActivate={start} />
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>{stage === "tunnel" && <Tunnel />}</AnimatePresence>

      <AnimatePresence>
        {stage === "done" && (
          <motion.div
            key="done"
            className="relative z-40 bg-gradient-to-r from-[#b81202] via-[#f6ecac] to-[#b81202] bg-clip-text text-xl font-bold tracking-tight text-transparent"
            style={{
              textShadow:
                "0 0 2px rgba(246,236,172,0.78), 0 0 8px rgba(184,18,2,0.82)",
            }}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
          >
            System Initialized
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
