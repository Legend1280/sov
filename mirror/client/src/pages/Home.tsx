import MirrorLayout from '@/components/MirrorLayout';
import ViewportPlaceholder from '@/components/ViewportPlaceholder';

export default function Home() {
  return (
    <MirrorLayout
      viewport1={<ViewportPlaceholder label="Viewport 1" />}
      viewport2={<ViewportPlaceholder label="Viewport 2" />}
    />
  );
}
