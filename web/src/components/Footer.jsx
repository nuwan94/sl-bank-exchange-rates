export default function Footer({ fetchedAt }) {
  return (
    <>
      <div className="border border-slate-200 bg-slate-50 px-4 py-4 sm:px-5 sm:py-5 shadow-sm">
        <p className="text-sm text-slate-600">
          Last updated{" "}
          <span className="font-semibold text-slate-900">
            {new Date(fetchedAt).toLocaleString()}
          </span>
        </p>
      </div>
      {/* footer credits */}
      <div className="flex flex-col sm:flex-row justify-between items-center mt-4 text-sm text-slate-600">
        <div className="block mb-1">
          <span>Made with ❤️ by </span>
          <a
            href="https://nuwan.dev"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:underline"
          >
            Nuwan
          </a>
        </div>

        <div className="block float-right">
          <span>Contribute on </span>
          <a
            href="https://github.com/nuwan94/sl-bank-exchange-rates"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:underline"
          >
          
            GitHub
          </a>
        </div>
      </div>
    </>
  );
}
