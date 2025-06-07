import { FcGoogle } from "react-icons/fc";
import { FaApple } from "react-icons/fa";
import { HiChevronLeft } from "react-icons/hi";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import StarLogo from "../assets/images/StarLogo.webp";
import Title from "../components/Title";
import { useSignUp, useLogIn } from "../hooks/useApi";
import { toast } from "react-hot-toast";
import { GoogleLoginButton } from "../components/GoogleLoginButton";

interface FieldErrors {
  name?: string;
  username?: string;
  email?: string;
  password?: string;
  confirmationPassword?: string;
}

export default function AuthentificationPage() {
  const navigate = useNavigate();
  const [isChecked, setIsChecked] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);

  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmationPassword, setConfirmationPassword] = useState("");

  const [errors, setErrors] = useState<FieldErrors>({});

  const {
    mutate: mutateSignUp,
    isError: signupError,
    error: signupErrorObj,
    isSuccess: signupSuccess,
    data: signUpResult,
  } = useSignUp();

  const {
    mutate: mutateLogIn,
    isError: loginError,
    error: loginErrorObj,
    isSuccess: loginSuccess,
    data: loginResult,
  } = useLogIn();

  useEffect(() => {
    if (signupError && signupErrorObj instanceof Error) {
      toast.error(signupErrorObj.message, {
        style: {
          borderRadius: "10px",
          background: "#1f1f1f",
          border: "1px solid #e53e3e",
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          color: "#fff",
          padding: "12px 16px",
          fontSize: "0.95rem",
        },
      });
    }
  }, [signupError, signupErrorObj]);

  useEffect(() => {
    if (signupSuccess && signUpResult) {
      toast.success("Account created successfully!", {
        style: {
          borderRadius: "10px",
          background: "#1f1f1f",
          border: "1px solid #6b46C1",
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          color: "#fff",
          padding: "12px 16px",
          fontSize: "0.95rem",
        },
      });
      toast.success("You can now log in. Redirecting...", {
        style: {
          borderRadius: "10px",
          background: "#1f1f1f",
          border: "1px solid #6b46C1",
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          color: "#fff",
          padding: "12px 16px",
          fontSize: "0.95rem",
        },
      });

      setTimeout(() => {
        setIsSignUp(false);
        setPassword("");
        setConfirmationPassword("");
        setErrors({});
      }, 1500);
    }
  }, [signupSuccess, signUpResult]);

  useEffect(() => {
    if (loginError && loginErrorObj instanceof Error) {
      toast.error(loginErrorObj.message, {
        style: {
          borderRadius: "10px",
          background: "#1f1f1f",
          border: "1px solid #e53e3e",
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          color: "#fff",
          padding: "12px 16px",
          fontSize: "0.95rem",
        },
      });
    }
  }, [loginError, loginErrorObj]);

  useEffect(() => {
    if (loginSuccess && loginResult) {
      toast.success("Logged in successfully!", {
        style: {
          borderRadius: "10px",
          background: "#1f1f1f",
          border: "1px solid #6b46C1",
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          color: "#fff",
          padding: "12px 16px",
          fontSize: "0.95rem",
        },
      });
      setTimeout(() => {
        navigate("/dashboard");
      }, 1000);
    }
  }, [loginSuccess, loginResult, navigate]);

  const validateFields = (): boolean => {
    const newErrors: FieldErrors = {};

    if (isSignUp) {
      if (!username.trim()) {
        newErrors.username = "Username is required.";
      }
      if (!name.trim()) {
        newErrors.name = "Full name is required.";
      }
      if (!email.trim()) {
        newErrors.email = "Email is required.";
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        newErrors.email = "Invalid email address.";
      }
      if (!password) {
        newErrors.password = "Password is required.";
      } else if (password.length < 8) {
        newErrors.password = "Password must be at least 8 characters.";
      }
      if (!confirmationPassword) {
        newErrors.confirmationPassword = "Please confirm your password.";
      } else if (password !== confirmationPassword) {
        newErrors.confirmationPassword = "Passwords do not match.";
      }
    } else {
      if (!email.trim()) {
        newErrors.email = "Email or username is required.";
      }
      if (!password) {
        newErrors.password = "Password is required.";
      }
    }

    setErrors(newErrors);

    const firstErrorKey = Object.keys(newErrors)[0] as
      | keyof FieldErrors
      | undefined;
    if (firstErrorKey && newErrors[firstErrorKey]) {
      toast.error(newErrors[firstErrorKey]!, {
        style: {
          borderRadius: "10px",
          background: "#1f1f1f",
          border: "1px solid #e53e3e",
          boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
          color: "#fff",
          padding: "12px 16px",
          fontSize: "0.95rem",
        },
      });
    }

    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrors({});

    if (isSignUp) {
      if (!validateFields()) return;

      mutateSignUp({
        name: name.trim(),
        username: username.trim(),
        email: email.trim(),
        password,
      });
    } else {
      if (!validateFields()) return;

      mutateLogIn({
        login: email.trim(),
        password,
      });
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 bg-gradient-to-b from-zinc-900/5 to-black/5 flex items-center justify-center px-4 py-8">
      <Title>{`Sign ${isSignUp ? "Up" : "In"} - Chathera`}</Title>
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[25%] -left-[25%] w-[150%] h-[150%] bg-gradient-conic from-violet-500/10 via-transparent to-transparent opacity-10 animate-slow-spin"></div>
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_800px_at_50%_50%,rgba(147,51,234,0.02),transparent)] animate-pulse"></div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative w-full max-w-md"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-zinc-500/5 to-zinc-400/5 rounded-2xl blur-2xl transform scale-105"></div>
        <div className="relative space-y-8 bg-black/20 backdrop-blur-xl p-8 rounded-2xl border border-white/5 shadow-2xl">
          <button
            onClick={() => navigate(-1)}
            className="absolute top-4 left-4 p-2 rounded-full bg-zinc-900/50 hover:bg-zinc-800/50 transition-colors text-gray-400 hover:text-gray-300"
            aria-label="Go back"
          >
            <HiChevronLeft className="w-5 h-5" />
          </button>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-center space-y-2"
          >
            <div className="flex justify-center mb-4">
              <img src={StarLogo} alt="StarLogo" className="w-8 h-8" />
            </div>
            <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-gray-200 to-white">
              {isSignUp ? "Create Account" : "Welcome Back"}
            </h2>
            <p className="text-gray-400">
              {isSignUp
                ? "Sign up to get started with Chathera"
                : "Sign in to continue to Chathera"}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-4"
          >
            <GoogleLoginButton>
              <button className="cursor-pointer w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg bg-black/40 hover:bg-black/50 border border-white/5 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg group">
                <FcGoogle className="text-xl transform transition-transform group-hover:scale-110" />
                <span className="text-white font-medium">
                  Continue with Google
                </span>
              </button>
            </GoogleLoginButton>
            <button
              onClick={() => console.log("Apple login clicked")}
              className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg bg-black/40 hover:bg-black/50 border border-white/5 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg group"
            >
              <FaApple className="text-xl text-white transform transition-transform group-hover:scale-110" />
              <span className="text-white font-medium">
                Continue with Apple
              </span>
            </button>
          </motion.div>

          <div className="relative">
            <div className="flex justify-center text-sm items-center">
              <div className="grow border-t border-white/10"></div>
              <span className="px-2 text-gray-400">Or continue with</span>
              <div className="grow border-t border-white/10"></div>
            </div>
          </div>

          <AnimatePresence mode="wait">
            <motion.form
              key={isSignUp ? "signup" : "signin"}
              initial={{ opacity: 0, x: isSignUp ? 20 : -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: isSignUp ? -20 : 20 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
              onSubmit={handleSubmit}
            >
              {isSignUp && (
                <>
                  <div className="group">
                    <label htmlFor="username" className="sr-only">
                      Username
                    </label>
                    <input
                      id="username"
                      name="username"
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className={`w-full px-4 py-3 rounded-lg bg-black/20 border ${
                        errors.username ? "border-red-500" : "border-white/10"
                      } text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-transparent transition-all duration-300`}
                      placeholder="Username"
                    />
                    {errors.username && (
                      <p className="mt-1 text-sm text-red-500">
                        {errors.username}
                      </p>
                    )}
                  </div>

                  <div className="group">
                    <label htmlFor="name" className="sr-only">
                      Full Name
                    </label>
                    <input
                      id="name"
                      name="name"
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className={`w-full px-4 py-3 rounded-lg bg-black/20 border ${
                        errors.name ? "border-red-500" : "border-white/10"
                      } text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-transparent transition-all duration-300`}
                      placeholder="Full Name"
                    />
                    {errors.name && (
                      <p className="mt-1 text-sm text-red-500">{errors.name}</p>
                    )}
                  </div>
                </>
              )}

              <div className="group">
                <label htmlFor="email" className="sr-only">
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`w-full px-4 py-3 rounded-lg bg-black/20 border ${
                    errors.email ? "border-red-500" : "border-white/10"
                  } text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-transparent transition-all duration-300`}
                  placeholder={isSignUp ? "Email" : "Email or Username"}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-500">{errors.email}</p>
                )}
              </div>

              {/* Password field */}
              <div className="group">
                <label htmlFor="password" className="sr-only">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`w-full px-4 py-3 rounded-lg bg-black/20 border ${
                    errors.password ? "border-red-500" : "border-white/10"
                  } text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-transparent transition-all duration-300`}
                  placeholder="Password"
                />
                {errors.password && (
                  <p className="mt-1 text-sm text-red-500">{errors.password}</p>
                )}
              </div>

              {isSignUp && (
                <div className="group">
                  <label htmlFor="confirmPassword" className="sr-only">
                    Confirm Password
                  </label>
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    value={confirmationPassword}
                    onChange={(e) => setConfirmationPassword(e.target.value)}
                    className={`w-full px-4 py-3 rounded-lg bg-black/20 border ${
                      errors.confirmationPassword
                        ? "border-red-500"
                        : "border-white/10"
                    } text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-transparent transition-all duration-300`}
                    placeholder="Confirm password"
                  />
                  {errors.confirmationPassword && (
                    <p className="mt-1 text-sm text-red-500">
                      {errors.confirmationPassword}
                    </p>
                  )}
                </div>
              )}

              {!isSignUp && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="relative">
                      <input
                        id="remember-me"
                        name="remember-me"
                        type="checkbox"
                        checked={isChecked}
                        onChange={(e) => setIsChecked(e.target.checked)}
                        className="peer sr-only"
                      />
                      <label
                        htmlFor="remember-me"
                        className="relative flex h-5 w-5 cursor-pointer items-center justify-center rounded-md border border-white/10 bg-black/20 transition-colors duration-300 hover:border-violet-500/30"
                      >
                        {isChecked && (
                          <span className="text-white text-base leading-none select-none">
                            ×
                          </span>
                        )}
                      </label>
                    </div>
                    <label
                      htmlFor="remember-me"
                      className="ml-2 block text-sm text-gray-400"
                    >
                      Remember me
                    </label>
                  </div>
                  <a
                    href="#"
                    className="text-sm text-violet-400 hover:text-violet-300 transition-colors"
                  >
                    Forgot password?
                  </a>
                </div>
              )}

              <button
                type="submit"
                className="relative w-full px-4 py-3 rounded-lg overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-violet-600/80 to-violet-700/80 transition-transform duration-300 group-hover:scale-[1.02]"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-violet-600/50 to-violet-700/50 opacity-50 blur-xl transition-transform duration-300 group-hover:scale-110"></div>
                <span className="relative text-white font-medium">
                  {isSignUp ? "Create Account" : "Sign in"}
                </span>
              </button>
            </motion.form>
          </AnimatePresence>

          <p className="text-center text-sm text-gray-400 mt-4">
            {isSignUp ? "Already have an account? " : "Don't have an account? "}
            <button
              onClick={() => {
                setIsSignUp(!isSignUp);
                setErrors({});
                setPassword("");
                setConfirmationPassword("");
              }}
              className="text-violet-400 hover:text-violet-300 transition-colors hover:underline cursor-pointer"
              type="button"
            >
              {isSignUp ? "Sign in" : "Sign up"}
            </button>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
