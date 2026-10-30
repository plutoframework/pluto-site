import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://plutoframework.github.io",
  base: "/pluto-site/docs",
  trailingSlash: "always",
  integrations: [
    starlight({
      title: "pluto. / field guide",
      description: "Build explicit Go APIs and React applications with Pluto.",
      customCss: ["./src/styles/pluto.css"],
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/plutoframework",
        },
      ],
      sidebar: [
        {
          label: "Start here",
          items: [
            { label: "Introduction", slug: "index" },
            { label: "Your first application", slug: "getting-started" },
            { label: "Worked examples", slug: "examples" },
            { label: "Configuration", slug: "configuration" },
            { label: "AI skills & Markdown", slug: "ai-skills" },
            { label: "Conventions & testing", slug: "conventions" },
            { label: "Deployment & upgrades", slug: "deployment" },
          ],
        },
        { label: "CLI", items: [{ autogenerate: { directory: "cli" } }] },
        {
          label: "Backend",
          items: [{ autogenerate: { directory: "backend" } }],
        },
        {
          label: "Frontend",
          items: [{ autogenerate: { directory: "frontend" } }],
        },
        { label: "Working example", slug: "example" },
        {
          label: "Product site ↗",
          link: "https://plutoframework.github.io/pluto-site/",
        },
      ],
    }),
  ],
});
