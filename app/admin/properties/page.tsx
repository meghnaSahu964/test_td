"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AdminLayout, adminApi } from "@/components/admin";

type Property = {
  id: number;
  title: string;
  location: string;
  property_type: string;
  price: number;
  status: string;
  featured: boolean;
  updated_at?: string;
  slug: string;
};

type PropertiesResponse = { data: Property[] };

const endpoint = "/api/v1/admin/properties";

function fetchProperties() {
  return adminApi<PropertiesResponse>(endpoint).then(({ data }) => data);
}

export default function PropertiesAdmin() {
  const [properties, setProperties] = useState<Property[] | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    let active = true;

    fetchProperties()
      .then((data) => {
        if (active) setProperties(data);
      })
      .catch(() => {
        if (active) setMessage("Unable to load properties.");
      });

    return () => {
      active = false;
    };
  }, []);

  async function reload() {
    try {
      setProperties(await fetchProperties());
    } catch {
      setMessage("Unable to load properties.");
    }
  }

  async function remove(id: number) {
    if (!confirm("Delete this property?")) return;

    try {
      await adminApi(`${endpoint}/${id}`, { method: "DELETE" });
      setMessage("Property deleted.");
      void reload();
    } catch {
      setMessage("Delete failed.");
    }
  }

  return (
    <AdminLayout>
      <div className="flex justify-between">
        <h1 className="text-3xl">Properties</h1>
        <Link
          className="bg-[#d4af37] px-4 py-2"
          href="/admin/properties/new"
        >
          Add Property
        </Link>
      </div>
      {message && <p className="mt-4">{message}</p>}
      {!properties ? (
        <p className="mt-8">Loading…</p>
      ) : properties.length === 0 ? (
        <p className="mt-8 bg-white p-8">No properties yet.</p>
      ) : (
        <div className="mt-8 overflow-x-auto bg-white">
          <table className="w-full text-left text-sm">
            <thead>
              <tr>
                {[
                  "Title",
                  "Location",
                  "Type",
                  "Price",
                  "Status",
                  "Featured",
                  "Updated",
                  "Actions",
                ].map((heading) => (
                  <th className="p-3" key={heading}>
                    {heading}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {properties.map((property) => (
                <tr className="border-t" key={property.id}>
                  <td className="p-3">{property.title}</td>
                  <td className="p-3">{property.location}</td>
                  <td className="p-3">{property.property_type}</td>
                  <td className="p-3">{property.price}</td>
                  <td className="p-3">{property.status}</td>
                  <td className="p-3">{property.featured ? "Yes" : "No"}</td>
                  <td className="p-3">{property.updated_at?.slice(0, 10)}</td>
                  <td className="whitespace-nowrap p-3">
                    <Link href={`/properties/${property.slug}`}>View</Link>{" "}
                    <Link href={`/admin/properties/${property.id}/edit`}>
                      Edit
                    </Link>{" "}
                    <button onClick={() => void remove(property.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AdminLayout>
  );
}
