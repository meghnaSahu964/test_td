"use client";

import { useEffect, useState } from "react";
import { AdminLayout, adminApi } from "@/components/admin";

type Enquiry = {
  id: number;
  name: string;
  email: string;
  phone: string;
  requirement: string;
  message: string;
  status: string;
};

type EnquiriesResponse = { data: Enquiry[] };

const states = ["new", "contacted", "qualified", "closed"];
const endpoint = "/api/v1/admin/enquiries";

function fetchEnquiries() {
  return adminApi<EnquiriesResponse>(endpoint).then(({ data }) => data);
}

export default function Enquiries() {
  const [enquiries, setEnquiries] = useState<Enquiry[] | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    let active = true;

    fetchEnquiries()
      .then((data) => {
        if (active) setEnquiries(data);
      })
      .catch(() => {
        if (active) setMessage("Unable to load enquiries.");
      });

    return () => {
      active = false;
    };
  }, []);

  async function reload() {
    try {
      setEnquiries(await fetchEnquiries());
    } catch {
      setMessage("Unable to load enquiries.");
    }
  }

  async function change(id: number, status: string) {
    try {
      await adminApi(`${endpoint}/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
      setMessage("Status saved.");
      void reload();
    } catch {
      setMessage("Update failed.");
    }
  }

  return (
    <AdminLayout>
      <h1 className="text-3xl">Enquiries</h1>
      {message && <p className="mt-3">{message}</p>}
      {!enquiries ? (
        <p className="mt-8">Loading…</p>
      ) : enquiries.length === 0 ? (
        <p className="mt-8 bg-white p-8">No enquiries yet.</p>
      ) : (
        <div className="mt-8 space-y-3">
          {enquiries.map((enquiry) => (
            <details className="bg-white p-5" key={enquiry.id}>
              <summary>
                {enquiry.name} · {enquiry.email} · {enquiry.status}
              </summary>
              <p className="mt-3">
                {enquiry.phone} · {enquiry.requirement}
              </p>
              <p className="mt-2">{enquiry.message}</p>
              <select
                className="mt-3 border p-2"
                value={enquiry.status}
                onChange={(event) =>
                  void change(enquiry.id, event.target.value)
                }
              >
                {states.map((status) => (
                  <option key={status}>{status}</option>
                ))}
              </select>
            </details>
          ))}
        </div>
      )}
    </AdminLayout>
  );
}
