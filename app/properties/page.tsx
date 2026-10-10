"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Button } from "@/components/site";
import { api } from "@/lib/api";

type Property = {
  title: string;
  slug: string;
  location?: string;
  property_type?: string;
  price?: number;
  currency?: string;
};

type Result = {
  data: Property[];
  meta: { page: number; pages: number };
};

type LoadedResult = { key: string; result: Result };

export default function Properties() {
  const [loaded, setLoaded] = useState<LoadedResult | null>(null);
  const [failedKey, setFailedKey] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const requestKey = `${page}:${query}`;
  const result = loaded?.key === requestKey ? loaded.result : null;
  const error = failedKey === requestKey;

  useEffect(() => {
    let active = true;

    api<Result>(
      `/api/v1/properties?page=${page}&search=${encodeURIComponent(query)}`,
    )
      .then((response) => {
        if (active) setLoaded({ key: requestKey, result: response });
      })
      .catch(() => {
        if (active) setFailedKey(requestKey);
      });

    return () => {
      active = false;
    };
  }, [page, query, requestKey]);

  return (
    <>
      <section className="bg-[#111] py-20 text-white">
        <div className="container">
          <p className="eyebrow text-[#d4af37]">Properties</p>
          <h1 className="mt-3 text-5xl">
            Explore available opportunities.
          </h1>
        </div>
      </section>
      <section className="container py-16">
        <input
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setPage(1);
          }}
          placeholder="Search properties"
          className="w-full border border-black/20 bg-white p-4"
        />
        {!result && !error && (
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {[1, 2, 3].map((item) => (
              <div
                className="h-52 animate-pulse bg-black/10"
                key={item}
              />
            ))}
          </div>
        )}
        {error && (
          <div className="mt-8 bg-white p-10 text-center">
            We’re unable to load properties right now. Please try again later.
          </div>
        )}
        {result?.data.length === 0 && (
          <div className="mt-8 border border-dashed border-black/25 bg-white px-6 py-20 text-center">
            <p className="eyebrow">Property listings</p>
            <h2 className="mt-3 text-4xl">Properties Coming Soon</h2>
            <p className="mx-auto mt-4 max-w-md leading-7 text-[#555]">
              Tell us what you’re looking for and our team can help you explore
              suitable opportunities.
            </p>
            <div className="mt-6">
              <Button href="/contact">Discuss Your Requirements</Button>
            </div>
          </div>
        )}
        {result && result.data.length > 0 && (
          <>
            <div className="mt-8 grid gap-5 md:grid-cols-3">
              {result.data.map((property) => (
                <Link
                  className="border border-black/15 bg-white p-6 transition hover:-translate-y-1"
                  href={`/properties/${property.slug}`}
                  key={property.slug}
                >
                  <p className="eyebrow">
                    {property.property_type || "Property"}
                  </p>
                  <h2 className="mt-3 text-2xl">{property.title}</h2>
                  {property.location && (
                    <p className="mt-2 text-sm text-[#555]">
                      {property.location}
                    </p>
                  )}
                  {property.price != null && (
                    <p className="mt-5 font-bold">
                      {property.currency || "₹"}{" "}
                      {property.price.toLocaleString()}
                    </p>
                  )}
                </Link>
              ))}
            </div>
            <div className="mt-8 flex justify-between">
              <button
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                Previous
              </button>
              <span>
                Page {page} of {result.meta.pages || 1}
              </span>
              <button
                disabled={page >= result.meta.pages}
                onClick={() => setPage(page + 1)}
              >
                Next
              </button>
            </div>
          </>
        )}
      </section>
    </>
  );
}
