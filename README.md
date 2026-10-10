# Amba Real Estate

## Install and develop

```bash
npm install
npm run dev
```

Build and validate with `npm run lint`, `npm run typecheck`, and `npm run build`.

## Production configuration

All public business details are centralized in `config/business.ts`. **Confirm the public address and phone with the owner before production**, then edit only that file. The official email is configured there as `hr@ambarealestate.co.in`; email delivery itself requires a configured provider or mailbox. The enquiry form validates in the browser and supplies a clear contact fallback; it does not send messages until a backend/provider is added.

Replace the text-based logo in `components/site.tsx` with the official asset when supplied. Stock imagery is deliberately labelled illustrative and can be replaced in `app/page.tsx`. Add verified listings to `data/properties.ts` and render them on `app/properties/page.tsx`; the typed property model is already available.

## Deploy to Vercel

1. Push this folder to a Git repository and import it at Vercel.
2. Select the repository; Vercel detects Next.js. Keep the build command as `npm run build`.
3. Deploy, then add `ambarealestate.co.in` and `www.ambarealestate.co.in` in Project Settings → Domains.
4. At the DNS provider, add the exact A/CNAME records Vercel displays. Choose a primary domain and redirect the other.

## Deploy to Cloudflare Pages

1. Push to Git and create a Pages project from the repository.
2. Use `npm run build` as the build command. For full Next.js server features, use Cloudflare's Next.js/OpenNext workflow; otherwise deploy through Vercel, which supports this application directly.
3. Add the custom domain in Pages, then add the CNAME/DNS records Cloudflare displays.

No domain, DNS, email mailbox, or delivery service has been configured by this project.
