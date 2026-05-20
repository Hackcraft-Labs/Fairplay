import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

@Component({
	selector: 'fp-empty-state',
	standalone: true,
	imports: [MatIconModule],
	templateUrl: './empty-state.html',
	styleUrl: './empty-state.scss'
})
export class EmptyStateComponent {
	@Input() icon = 'search_off';
	@Input() title = 'Nothing to show yet';
	@Input() body = 'Try adjusting filters or adding new items.';
}