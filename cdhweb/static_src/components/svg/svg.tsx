import { JSX } from 'react';
import { staticSVGRoot } from '../../constants';

type SvgProps = {
  sprite: string;
  svg: string;
  className?: string;
  ariaHidden?: boolean;
};

/**
 * Use this `<Svg />` component when you need to render an SVG in a React component.
 * `sprite` = the directory that the svg file lives in, e.g. 'global' or 'logos' etc.
 * `svg` = the name of the svg file (minus extension), e.g. hamburger.svg would be passed in as "hamburger".
 * `className` = CSS class(es), probably BEM, to make your SVG look correct.
 * `ariaHidden` = defaults to true. You likely won't need to override this.
 */
export const Svg = ({
  sprite,
  svg,
  className,
  ariaHidden = true,
}: SvgProps): JSX.Element => {
  return (
    <svg className={className || undefined} aria-hidden={ariaHidden}>
      <use href={`${staticSVGRoot}${sprite}.svg#${svg}`} />
    </svg>
  );
};

export default Svg;
