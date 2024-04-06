import { serve, ServerRequest } from "https://deno.land/std/http/server.ts";

const getAddress = (url: URL) => {
  return url.searchParams.get("addr");
};

const getLatitudeAndLongitude = (url: URL) => {
  return {
    latitude: url.searchParams.get("lat"),
    longitude: url.searchParams.get("long")
  };
};

async function handleRequest(req: ServerRequest) {
  const url = new URL(req.url, `http://${req.headers.get("host")}/`);
  let response: string;

  if (url.pathname === "/addr") {
    const address = getAddress(url);
    response = address ? `Address: ${address}` : "Please provide an address.";
  } else if (url.pathname === "/lat") {
    const { latitude, longitude } = getLatitudeAndLongitude(url);
    response = latitude && longitude
      ? `Latitude: ${latitude}, Longitude: ${longitude}`
      : "Please provide both latitude and longitude.";
  } else {
    response = "Invalid API endpoint.";
  }

  req.respond({ body: response });
};

const PORT = 8000;
const server = serve({ port: PORT });
console.log(`Server running on port ${PORT}`);

for await (const req of server) {
  handleRequest(req);
}
