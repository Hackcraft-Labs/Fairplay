import { Component, Input } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
	selector: 'fp-loading-spinner',
	standalone: true,
	imports: [MatProgressSpinnerModule],
	template: `
		@if (visible) {
			<div class="fp-loading">
				<mat-progress-spinner mode="indeterminate" [diameter]="50"></mat-progress-spinner>
			</div>
		}
	`,
	styles: [
		`
		.fp-loading {
			display: flex;
			align-items: center;
			justify-content: center;
			padding: var(--fp-space-6);
		}

		.fp-loading :is(mat-progress-spinner, .mat-mdc-progress-spinner) {
			--mdc-circular-progress-active-indicator-color: var(--fp-accent);
		}
		`
	]
})
export class LoadingSpinnerComponent {
  	@Input() visible = false;
}