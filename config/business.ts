/** CONFIRM PUBLIC BUSINESS ADDRESS AND PHONE WITH OWNER BEFORE PRODUCTION. */
export const business = {
  name: "Amba Real Estate",
  website: "https://ambarealestate.co.in",
  email: "hr@ambarealestate.co.in",
  phone: "098111 96755",
  phoneHref: "tel:+919811196755",
  address: { street: "Rail Vihar, 1287-U, Block H, Sector 57", city: "Gurugram", state: "Haryana", postalCode: "122011", country: "India" },
  services: ["Property Buying", "Luxury Properties", "Property Investment", "Property Consulting", "International Property Buying"],
};
export const addressLine = `${business.address.street}, ${business.address.city}, ${business.address.state} ${business.address.postalCode}, ${business.address.country}`;
export const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${business.name}, ${addressLine}`)}`;
