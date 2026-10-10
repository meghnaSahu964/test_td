const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export class ApiError extends Error { constructor(public status: number, message: string) { super(message); } }
export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, { ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: unknown } | null;
    let detail: string | undefined;
    if (typeof body?.detail === "string") {
      detail = body.detail;
    } else if (Array.isArray(body?.detail)) {
      const errors = body.detail.flatMap((item: unknown) => {
        if (typeof item !== "object" || item === null || !("msg" in item) || typeof item.msg !== "string") {
          return [];
        }

        const location = "loc" in item && Array.isArray(item.loc)
          ? item.loc.filter((part: unknown) => part !== "body").join(".")
          : "";
        return [location ? `${location}: ${item.msg}` : item.msg];
      });
      if (errors.length > 0) detail = `Please check: ${errors.join("; ")}`;
    } else if (
      typeof body?.detail === "object" &&
      body.detail !== null &&
      "message" in body.detail &&
      typeof body.detail.message === "string"
    ) {
      detail = body.detail.message;
    }

    throw new ApiError(response.status, detail || "The enquiry could not be submitted.");
  }
  return response.json() as Promise<T>;
}
