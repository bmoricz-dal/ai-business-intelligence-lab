/** Public website Worker. Binding types are generated from the build config. */
import { handleImageOptimization, DEFAULT_DEVICE_SIZES, DEFAULT_IMAGE_SIZES } from "vinext/server/image-optimization";
import handler from "vinext/server/app-router-entry";
import { newsRequest } from "./news";
import { reviewRequest } from "./review";
import { researchRequest } from "./research";
import { withNewsDatabase } from "../db/news";

const worker = {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const research = await researchRequest(request, env);
    if (research) return research;
    const review = await reviewRequest(request, env);
    if (review) return review;
    const news = await newsRequest(request, env);
    if (news) return news;
    if (url.pathname === "/_vinext/image") {
      // No Images binding is configured. Serve the validated original asset;
      // do not attempt a transformation through an unavailable paid binding.
      return handleImageOptimization(request, {
        fetchAsset: (path) => env.ASSETS.fetch(new Request(new URL(path, request.url))),
      }, [...DEFAULT_DEVICE_SIZES, ...DEFAULT_IMAGE_SIZES]);
    }
    return withNewsDatabase(env.DB, () => handler.fetch(request, env, ctx));
  },
} satisfies ExportedHandler<Cloudflare.Env>;

export default worker;
