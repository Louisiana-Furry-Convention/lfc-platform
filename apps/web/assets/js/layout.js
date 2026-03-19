export async function loadLayout() {
  const res = await fetch("/components/layout.html");
  const html = await res.text();

  document.body.innerHTML = html;

  return true;
}
