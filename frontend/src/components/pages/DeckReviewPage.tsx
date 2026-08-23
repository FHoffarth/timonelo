import DeckReviewWorkspace from '../../deck-review/DeckReviewWorkspace';

export default function DeckReviewPage() {
  return (
    <div className="w-full flex-1 bg-[#FBF8F3]">
      <DeckReviewWorkspace initialDeckNumber={5} />
    </div>
  );
}
