import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#f9f9f9] text-center p-8">
      <header className="py-16">
        <h1 className="text-4xl font-bold">UNFINDABLES</h1>
        <p className="text-lg mt-4 text-gray-600">
          Obscure but useful websites, tools, and digital gems for indie devs
        </p>
      </header>
      <main className="max-w-2xl mx-auto">
        <h2 className="text-2xl font-semibold mb-4">
          Discover hidden treasures of the internet
        </h2>
        <p className="text-gray-700 mb-8">
          Unfindables curates under-the-radar content to help indie devs find inspiration, ideas, and clever tools hidden in the corners of the internet.
        </p>
        <form className="flex justify-center items-center gap-2">
          <input
            type="email"
            placeholder="Email address"
            className="border border-gray-300 rounded px-4 py-2 w-full max-w-sm"
          />
          <button
            type="submit"
            className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800"
          >
            Subscribe
          </button>
        </form>
      </main>
      <section className="mt-16">
        <h3 className="text-xl font-semibold">Featured</h3>
        {/* Add featured content here */}
      </section>
    </div>
  );
}
