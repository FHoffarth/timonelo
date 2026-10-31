import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import MainNavbar from "./MainNavbar";

describe("responsive main navigation", () => {
  it("provides every existing destination inside an initially closed native disclosure", () => {
    const html = renderToStaticMarkup(<MainNavbar currentRoute="home" onNavigate={() => {}} />);
    const mobile = html.slice(html.indexOf("<details"), html.indexOf("</details>"));
    expect(mobile).toContain('aria-label="Mobile main navigation"');
    expect(mobile).not.toMatch(/<details[^>]*\bopen(?:=|\s|>)/);
    for (const label of ["Home", "Ships", "Ports", "Routes", "Cruise Math", "Travel Info", "My Cruise"]) {
      expect(mobile).toContain(`>${label}</button>`);
    }
  });

  it("identifies the active mobile destination and keeps the desktop navigation", () => {
    const html = renderToStaticMarkup(<MainNavbar currentRoute="ports" onNavigate={() => {}} />);
    expect(html).toMatch(/<button[^>]*aria-current="page"[^>]*>Ports<\/button>/);
    expect(html).toContain('aria-label="Main navigation"');
    expect(html).toContain('aria-label="Search intelligence"');
  });
});
