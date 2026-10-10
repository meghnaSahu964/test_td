"use client";

import { useEffect, useState } from "react";
import { AdminLayout, adminApi } from "@/components/admin";

type Consultation = {
  id: number;
  name: string;
  email: string;
  phone: string;
  requirement: string;
  preferred_contact_method: string;
  message: string;
  status: string;
};

type ConsultationsResponse = { data: Consultation[] };

const states = ["new", "contacted", "qualified", "closed"];
const endpoint = "/api/v1/admin/consultations";

function fetchConsultations() {
  return adminApi<ConsultationsResponse>(endpoint).then(({ data }) => data);
}

export default function Consultations() {
  const [consultations, setConsultations] = useState<Consultation[] | null>(
    null,
  );
  const [message, setMessage] = useState("");

  useEffect(() => {
    let active = true;

    fetchConsultations()
      .then((data) => {
        if (active) setConsultations(data);
      })
      .catch(() => {
        if (active) setMessage("Unable to load consultations.");
      });

    return () => {
      active = false;
    };
  }, []);

  async function reload() {
    try {
      setConsultations(await fetchConsultations());
    } catch {
      setMessage("Unable to load consultations.");
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
      <h1 className="text-3xl">Consultations</h1>
      {message && <p className="mt-3">{message}</p>}
      {!consultations ? (
        <p className="mt-8">Loading…</p>
      ) : consultations.length === 0 ? (
        <p className="mt-8 bg-white p-8">No consultation requests yet.</p>
      ) : (
        <div className="mt-8 space-y-3">
          {consultations.map((consultation) => (
            <details className="bg-white p-5" key={consultation.id}>
              <summary>
                {consultation.name} · {consultation.email} ·{" "}
                {consultation.status}
              </summary>
              <p className="mt-3">
                {consultation.phone} · {consultation.requirement} ·{" "}
                {consultation.preferred_contact_method}
              </p>
              <p className="mt-2">{consultation.message}</p>
              <select
                className="mt-3 border p-2"
                value={consultation.status}
                onChange={(event) =>
                  void change(consultation.id, event.target.value)
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
