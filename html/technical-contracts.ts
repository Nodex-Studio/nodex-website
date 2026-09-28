/** Nodex native architecture proposal, contract v1. Not an implemented SDK. */
export type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
export type Id = string;
export type RunStatus = 'queued' | 'planning' | 'editing' | 'building' | 'testing'
  | 'awaiting_approval' | 'ready' | 'failed' | 'cancelled' | 'superseded';

export interface Project {
  id: Id;
  draftRevisionId: Id | null; // Redacted to null for viewers.
  publishedReleaseId: Id | null;
  publishedConfigurationVersion: number | null;
  version: number;
}
export interface AuthoringRequest {
  prompt: string;
  baseRevisionId: Id;
  selectedComponentId?: Id;
}
export interface AuthoringRun {
  id: Id;
  projectId: Id;
  baseRevisionId: Id;
  status: RunStatus;
  attempt: number;
  candidateRevisionId: Id | null;
  releaseId: Id | null;
  failure: ApiError['error'] | null;
}
export interface SourceRevision {
  id: Id;
  projectId: Id;
  parentRevisionId: Id | null;
  treeHash: string;
  lockfileHash: string;
  createdByRunId: Id | null;
}
export interface ReleaseManifest {
  schemaVersion: 1;
  releaseId: Id;
  projectId: Id;
  sourceRevisionId: Id;
  runtimeApiMajor: 1;
  format: 'iife-register';
  entry: string; // Relative path inside immutable release directory.
  styles: string[];
  assets: { path: string; sha256: string; bytes: number }[];
  stateSchemaVersion: number;
  requiredOperations: string[]; // Declaration; never a permission grant.
}
export interface Release {
  id: Id;
  buildId: Id;
  projectId: Id;
  sourceRevisionId: Id;
  status: 'awaiting_approval' | 'approved' | 'rejected' | 'revoked';
  manifest: ReleaseManifest;
}
export interface RevisionEvent {
  eventId: Id;
  type: 'run.updated' | 'release.approved' | 'release.revoked' | 'publication.updated' | 'resync.required';
  projectId: Id;
  runId?: Id;
  releaseId?: Id;
  sequence: number;
  occurredAt: string; // RFC 3339 UTC timestamp.
}
export interface ApiError {
  error: {
    code: string;
    message: string;
    retryable: boolean;
    requestId: Id;
    details?: Record<string, Json>;
  };
}
export interface SavedState {
  schemaVersion: number;
  data: Record<string, Json>;
}
export interface QueryRequest {
  operationId: string;
  parameters: Record<string, Json>;
  cursor?: string;
  pageSize?: number;
}
export interface QueryResult {
  requestId: Id;
  columns: { name: string; type: 'string' | 'number' | 'boolean' | 'date' | 'datetime' | 'decimal' }[];
  rows: Record<string, Json>[];
  nextCursor: string | null;
  truncated: boolean;
  modelVersion: string;
  asOf: string;
}
export interface RuntimeContext {
  instanceId: Id;
  projectId: Id;
  releaseId: Id;
  mode: 'preview' | 'published' | 'snapshot';
  phase: 'staging' | 'active';
  theme: 'light' | 'dark';
  locale: string;
  timezone: string;
  scopeClass: string;
  initialState: SavedState | null;
  configuration: RuntimeConfiguration;
  sdk: NodexSDK;
  signal: AbortSignal;
}
export interface NodexSDK {
  query(request: QueryRequest, options?: { signal?: AbortSignal }): Promise<QueryResult>;
  report(event: { kind: 'error' | 'warning'; code: string; message: string }): void;
}
export interface ReadyResult {
  status: 'ready' | 'empty';
  restoredState: boolean;
  warnings: string[];
}
export interface DashboardHandle {
  ready: Promise<ReadyResult>;
  updateContext(next: Pick<RuntimeContext, 'theme' | 'locale' | 'timezone' | 'phase' | 'configuration'>): Promise<void>;
  serializeState(): SavedState;
  restoreState(state: SavedState): Promise<{ restored: boolean }>;
  dispose(): Promise<void>;
}
export interface DashboardModule {
  runtimeApiMajor: 1;
  mount(container: HTMLElement, context: RuntimeContext): DashboardHandle;
}
export interface DashboardRegistration {
  projectId: Id;
  releaseId: Id;
  runtimeApiMajor: 1;
  create(): DashboardModule;
}
/** Persistent host registry. Register is the bundle's only top-level effect. */
export interface NodexBundleRegistry {
  register(registration: DashboardRegistration): void;
}
export interface RuntimeConfiguration {
  releaseId: Id;
  configVersion: number;
  values: Record<string, Json>;
}
export interface ModelDescriptor {
  id: Id;
  version: string;
  label: string;
  fields: { id: Id; label: string; kind: 'dimension' | 'measure'; dataType: string }[];
  operations: { id: Id; parameterSchema: Json }[];
}
/** Server-only adapter: never shipped to generated apps. */
export interface AnalyticsAdapter {
  describeModels(identity: AuthorizedIdentity): Promise<ModelDescriptor[]>;
  execute(identity: AuthorizedIdentity, request: QueryRequest, signal: AbortSignal): Promise<QueryResult>;
}
export interface AuthorizedIdentity {
  tenantId: Id;
  userId: Id;
  permissionVersion: string;
}
