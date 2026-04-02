import { cookies } from "next/headers";

import { fetchCurrentUser, fetchMyCompanyProfile } from "./api";

async function getCookieHeader() {
  const cookieStore = await cookies();
  return cookieStore
    .getAll()
    .map((item) => `${item.name}=${item.value}`)
    .join("; ");
}

export async function getCookieHeaderFromSession() {
  return getCookieHeader();
}

export async function getCurrentUserFromSession() {
  const cookieHeader = await getCookieHeader();

  return fetchCurrentUser(cookieHeader || undefined).catch(() => null);
}

export async function getMyCompanyProfileFromSession() {
  const cookieHeader = await getCookieHeader();
  return fetchMyCompanyProfile(cookieHeader || undefined).catch(() => null);
}
