# Website editing and deployment

This folder contains the public SME Intelligence Lab website. It is a
Cloudflare Workers application built with vinext.

## First setup

Open Terminal and run:

```bash
git clone https://github.com/bmoricz-dal/ai-business-intelligence-lab.git
cd ai-business-intelligence-lab/website
npm install
code .
```

If `code .` is not recognised, open Visual Studio Code, choose **File → Open
Folder**, and select the `website` folder.

## Edit the website

The two main files are:

- `app/page.tsx` - page wording, links, reports and sections;
- `app/globals.css` - colours, spacing, typography and mobile layout.

Start a local preview from Terminal:

```bash
npm run dev
```

Open the local address shown in Terminal, normally
`http://localhost:3000`. Save a file in Visual Studio Code and refresh the
browser to see the change.

## Check before publishing

Stop the preview with `Control+C`, then run:

```bash
npm test
```

This builds the production version and checks the public wording, report links,
denominators, evidence limits and navigation.

## Deploy to Cloudflare Workers

The first time only, sign in:

```bash
npx wrangler login
```

After a successful test, deploy:

```bash
npm run deploy
```

The deploy script targets the Worker named `ai-business-intelligence-lab`.
Check the Cloudflare output before confirming that the live site has changed.

## Save the source on GitHub

From the repository root:

```bash
git status
git add website
git commit -m "Update public website"
git push
```

Deployment changes the public website. Run it only after you have reviewed the
local preview and the tests pass.
