import React, { createContext, useContext, useState, useEffect } from "react";

export type ThemeMode = "night" | "day";

interface ThemeContextType {
  theme: ThemeMode;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: "night",
  toggleTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<ThemeMode>("night");

  const toggleTheme = () => {
    setTheme((prev) => (prev === "night" ? "day" : "night"));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className={theme === "night" ? "dark bg-slate-950 text-slate-100" : "light bg-slate-100 text-slate-900"}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
};
