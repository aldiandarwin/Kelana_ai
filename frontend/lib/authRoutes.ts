// Keep public information/error pages available when there is no session.
// Backend authorization remains the security boundary for user data.
export function requiresAuthentication(pathname: string): boolean {
  return pathname === "/" || ["/trips", "/assistant", "/chat", "/profile"]
    .some((route) => pathname === route || pathname.startsWith(route + "/"));
}
