import { Component, Input } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
	selector: 'fp-button',
	standalone: true,
	imports: [MatButtonModule, MatIconModule],
	templateUrl: './button.html'
})
export class ButtonComponent {
	@Input() color: 'primary' | 'accent' | 'warn' | undefined = 'primary';
	@Input() icon?: string;
	@Input() type: 'button' | 'submit' = 'button';
}