<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

- Keep the existing research tools on their own routes and compose the scrolling homepage from reusable API-backed views, so the editorial presentation does not replace the complete console.
- All frontend requests stay in the centralized API service; preserve DEMO/LIVE switching and never implement filesystem or model computation in presentation code.
