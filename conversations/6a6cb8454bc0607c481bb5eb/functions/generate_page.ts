import { base44 } from './base44';

/**
 * Generate a web page from a specification.
 * Invokes the web-artifacts-builder skill workflow.
 */
export default async function generate_page(spec: {
  title: string;
  type: 'landing_page' | 'dashboard' | 'explorer' | 'docs' | 'component';
  project: 'verdis' | 'evolvixos';
  framework?: 'react' | 'html';
  theme_id?: string;
  description?: string;
}) {
  // Validate project
  if (!spec.project || !['verdis', 'evolvixos'].includes(spec.project)) {
    throw new Error('project must be "verdis" or "evolvixos"');
  }

  // Fetch the appropriate theme
  let theme = null;
  if (spec.theme_id) {
    const themes = await base44.entities.ThemeProfile.list();
    theme = themes.find((t: any) => t.id === spec.theme_id);
  }
  if (!theme) {
    const themes = await base44.entities.ThemeProfile.list();
    theme = themes.find((t: any) => 
      t.project === spec.project && t.is_default
    ) || themes.find((t: any) => t.is_dark_first && t.is_default);
  }

  // Create web_artifact record
  const artifact = await base44.entities.WebArtifact.create({
    title: spec.title,
    type: spec.type,
    project: spec.project,
    framework: spec.framework || 'html',
    theme_id: theme?.id,
    description: spec.description || '',
    status: 'draft',
    a11y_score: 0,
    consistency_score: 0,
  });

  return {
    artifact_id: artifact.id,
    theme: theme ? {
      name: theme.name,
      color_tokens: theme.color_tokens,
      typography: theme.typography,
      radius: theme.radius,
      spacing_scale: theme.spacing_scale,
    } : null,
    project: spec.project,
    deploy_target: spec.project === 'verdis' 
      ? '91.98.160.145:/opt/verdis-repo/dist/web/'
      : '62.238.61.145:/opt/evolvixos/frontend-v2/dist/',
    status: 'draft',
    message: `Artifact "${spec.title}" created. Theme: ${theme?.name || 'default'}. Ready for design generation.`,
  };
}
