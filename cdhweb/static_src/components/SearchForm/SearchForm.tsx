import { useId } from 'react';
import cx from 'classnames';

type Props = {
  searchUrl: string;
  extraClasses?: string;
};
/**
 * TSX version of search_form.html, for when used in React components like the main nav.
 */
const SearchForm = ({ searchUrl, extraClasses }: Props): JSX.Element => {
  const uniqueId = useId();

  return (
    <form className={cx('search-form', extraClasses)} action={searchUrl}>
      <label className="sr-only" htmlFor={`search-input_${uniqueId}`}>
        Search
      </label>
      <div className="text-input-and-button-group">
        <input type="text" id={`search-input_${uniqueId}`} name="q" />
        <input type="submit" value="Search" />
      </div>
      <fieldset className="search-form__filters">
        <legend className="sr-only">Filter search results by</legend>
        <div className="search-form__radio">
          <input
            type="radio"
            name="filter"
            id={`${uniqueId}_everything`}
            checked
          />
          <label htmlFor={`${uniqueId}_everything`}>Everything</label>
        </div>
        <div className="search-form__radio">
          <input type="radio" name="filter" id={`${uniqueId}_people`} />
          <label htmlFor={`${uniqueId}_people`}>People</label>
        </div>
        <div className="search-form__radio">
          <input type="radio" name="filter" id={`${uniqueId}_projects`} />
          <label htmlFor={`${uniqueId}_projects`}>Projects</label>
        </div>
        <div className="search-form__radio">
          <input type="radio" name="filter" id={`${uniqueId}_events`} />
          <label htmlFor={`${uniqueId}_events`}>Events</label>
        </div>
        <div className="search-form__radio">
          <input
            type="radio"
            name="filter"
            id={`${uniqueId}_blogs-and-news"`}
          />
          <label htmlFor={`${uniqueId}_blogs-and-news"`}>Blogs & news</label>
        </div>
      </fieldset>
    </form>
  );
};

export default SearchForm;
